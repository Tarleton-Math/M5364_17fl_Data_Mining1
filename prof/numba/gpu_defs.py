import math
import numba as nb
import numba.cuda as cuda
nb_dtype = nb.float32
threads_per_block_max = 1024
sqrt_threads_per_block_max = int(np.floor(np.sqrt(threads_per_block_max)))

num_walls = len(wall)
num_part = part.num
pp_bcols = min(num_part, sqrt_threads_per_block_max)
pp_brows = pp_bcols
pp_gcols = int(np.ceil(num_part / pp_bcols))
pp_grows = pp_gcols
pp_block_shape = (pp_bcols, pp_brows)
pp_grid_shape = (pp_gcols, pp_grows)
assert pp_block_shape[1] * pp_grid_shape[1] >= num_part
assert pp_block_shape[0] == pp_block_shape[1]
assert pp_grid_shape[0] == pp_grid_shape[1]

pw_bcols = num_walls
pw_brows = int(np.floor(threads_per_block_max / pw_bcols))
pw_gcols = 1
pw_grows = int(np.ceil(num_part / pw_brows))
pw_block_shape = (pw_bcols, pw_brows)
pw_grid_shape = (pw_gcols, pw_grows)
assert pw_block_shape[1] * pw_grid_shape[1] >= num_part
assert pw_block_shape[0] * pw_grid_shape[0] >= num_walls

def disp_gpu(A):
    B = A.get('host')
    C = A.get('gpu').copy_to_host()
    print('host')    
    print(B)
    print('device')    
    print(C)
    assert np.allclose(B,C)


def load_gpu(part):
    print('load_gpu')

    if part.num < part.dim:
        raise Exception('Can not use parallel processing when part_num < dim')

    part.radius_gpu = cuda.to_device(part.radius)

#     part.pos_smrt = nb.SmartArray(part.pos, copy=False)
#     part.pos = part.pos_smrt.get('host')

    part.pos_smrt = nb.SmartArray(part.pos)
    part.pos = part.pos_smrt.get('host')

    part.vel_smrt = nb.SmartArray(part.vel)
    part.vel = part.vel_smrt.get('host')

    part.pp_mask_smrt = nb.SmartArray(part.pp_mask)
    part.pp_mask = part.pp_mask_smrt.get('host')
    
    part.pw_mask_smrt = nb.SmartArray(part.pw_mask)
    part.pw_mask = part.pw_mask_smrt.get('host')
    
    part.pp_dt_block = np.full([part.num, pp_grid_shape[0]], np.inf, dtype=np_dtype)
    part.pp_dt_block_smrt = nb.SmartArray(part.pp_dt_block)

#     part.wall_base_point_gpu = cuda.to_device(np.vstack([w.base_point for w in wall]))
#     part.wall_normal_gpu = cuda.to_device(np.vstack([w.normal for w in wall]))
#     part.pw_gap_min_gpu = cuda.to_device(np.vstack([w.pw_gap_min for w in wall]))

def sync(cpu, smrt):
    assert np.allclose(cpu,smrt.get('host'), rtol=0.01)
    assert np.allclose(cpu,smrt.get('gpu'), rtol=0.01)

def check_sync():
    sync(part.pos, part.pos_smrt)
    sync(part.vel, part.vel_smrt)
    sync(part.pw_mask, part.pw_mask_smrt)
    sync(part.pp_mask, part.pp_mask_smrt)

def update_gpu(part):
    part.pos_smrt.mark_changed()
    part.vel_smrt.mark_changed()
    part.pw_mask_smrt.mark_changed()
    part.pp_mask_smrt.mark_changed()
#     cuda.synchronize()
    
def get_pp_col_time_gpu(part):
    get_pp_col_time_kernel[pp_grid_shape, pp_block_shape](part.pp_dt_block_smrt, part.pos_smrt, part.vel_smrt, part.pp_mask_smrt, part.num, part.radius_gpu)#, part.pp_dt_full_gpu, part.pp_a_gpu, part.pp_b_gpu, part.pp_c_gpu)
    part.pp_dt_gpu = np.min(part.pp_dt_block_smrt.get('gpu'), axis=1)
#     cuda.synchronize()
#     part.get_pp_col_time_cpu()
#     assert np.allclose(part.pp_dt, part.pp_dt_gpu, rtol=0.01)
    part.pp_dt = part.pp_dt_gpu.copy()

    
@cuda.jit
def get_pp_col_time_kernel(pp_dt, pos, vel,  mask, N, radius):#, pp_dt_full, a_gpu, b_gpu, c_gpu):
    pp_dt_shr = cuda.shared.array(shape=(pp_brows, pp_bcols), dtype=nb_dtype)
    tx = cuda.threadIdx.x
    ty = cuda.threadIdx.y
    p = ty + cuda.blockIdx.y * cuda.blockDim.y
    q = tx + cuda.blockIdx.x * cuda.blockDim.x
    if ((p >= N) or (q >= N)):        
        pp_dt_shr[ty,tx] = np.inf
        a = p
        b = q
        c = N
    else:
        a = 0.0
        b = 0.0
        c = 0.0
        for d in range(dim):
            dx = pos[p,d] - pos[q,d]
            dv = vel[p,d] - vel[q,d]
            a += (dv * dv)
            b += (dx * dv * 2)
            c += (dx * dx)
        c -= (radius[p] + radius[q])**2

        if ((mask[0]==p) & (mask[1]==q)):
            masked = True
        elif ((mask[0]==q) & (mask[1]==p)):
            masked = True
        else:
            masked = False

        pp_dt_shr[ty,tx] = solve_quadratic_gpu(a, b, c, masked)

    cuda.syncthreads()

    row_min_gpu(pp_dt_shr)
    pp_dt[p, cuda.blockIdx.x] = pp_dt_shr[ty, 0]
    cuda.syncthreads()

#         a_gpu[p,q] = pos[p,0]
#         b_gpu[p,q] = pos[p,1]
#         c_gpu[p,q] = pos[p,2]
#         pp_dt_full[p,q] = pp_dt_shr[ty,tx]

        
        
@cuda.jit(device=True)
def solve_quadratic_gpu(a, b, c, mask=False):
    tol = 1e-5
    small = np.inf
    big = np.inf
    b *= -1
    if abs(a) < tol:
        if abs(b) >= tol:
            small = c / b
    else:
        d = b**2 - 4 * a * c
        if d >= 0:
            d = math.sqrt(d)
            f = 2 * a
            if b >= 0:
                small = (b - d) / f
                big  =  (b + d) / f
            else:
                small = (b + d) / f
                big  =  (b - d) / f
#     if mask == True:
#         small = big
#         big = np.inf
#     if small < 0:
#         if big < 0:
#             small = np.inf
# #             big = np.inf
#         else:
#             small = big
# #             big = np.inf
#     return small

    if mask == True:
        small = np.inf
    if small < 0:
        small = np.inf
    if big < 0:
        big = np.inf
    return min(small, big)



@cuda.jit(device=True)
def row_min_gpu(A):
    tx = cuda.threadIdx.x
    ty = cuda.threadIdx.y
    m = float(cuda.blockDim.x)
    while m > 1:
        n = m / 2
        k = int(math.ceil(n))
        if (tx + k) < m:
            if A[ty,tx] > A[ty,tx+k]:
                A[ty,tx] = A[ty,tx+k]
        m = n
        cuda.syncthreads()