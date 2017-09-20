def dist(A, B, p=2):
    D = (A[:,np.newaxis,:] - B[np.newaxis,:,:])
    if p%2 != 0:
        D = np.abs(D)
    D **= p
    D = np.einsum('ijk->ij',D)
    if p == 2:
        return np.sqrt(D)
    else:
        return D**(1/p)

def my_knn1(k, normalize=False):    
    D = dist(feat_old, feat_new)
    srt = np.argpartition(D, k, axis=0)[:k]
    votes = pd.DataFrame(targ_old[srt])

    def compute_freq(c):
        return c.value_counts(normalize = normalize)    
    freq = votes.apply(compute_freq).fillna(0).T
    if normalize == False:
        freq = freq.astype(int,copy=False)
    return freq


def my_knn2(k, normalize=False):
    D = dist(feat_old, feat_new)
    srt = np.argpartition(D, k-1, axis=0)[:k]
    votes = targ_old[srt]
    
    freq = np.array([(votes == l).sum(axis=0) for l in range(len(levels))]).T
    if normalize == True:
        freq = freq.astype(float,copy=False)
        freq /= k
    return freq


def my_knn3(k, normalize=False):
    D = dist(feat_old, feat_new)
    srt = np.argpartition(D, k-1, axis=0)[:k]
    votes = targ_old[srt]
    
    freq = np.array([np.einsum('ij->j',(votes == l).astype(int)) for l in range(len(levels))]).T
    if normalize == True:
        freq = freq.astype(float,copy=False)
        freq /= k
    return freq


from sklearn.neighbors import KNeighborsClassifier
def sk_knn(k):
    knn_class = skl.neighbors.KNeighborsClassifier(n_neighbors=k)
    knn_class.fit(feat_old, targ_old)
    return knn_class.predict_proba(feat_new)    
    

from setup import *
k = 45
normalize = True
iris = sns.load_dataset('iris')
feat_old = iris[['sepal_length','sepal_width','petal_length','petal_width']].values
feat_new = iris.groupby('species').mean().values

t = iris['species'].factorize()
targ_old = t[0]
levels = t[1].tolist()


my_freq1 = my_knn1(k,normalize)
my_freq1.columns = levels
display(my_freq1)

my_freq2 = my_knn2(k,normalize)
display(pd.DataFrame(my_freq2,columns=levels))

my_freq3 = my_knn3(k,normalize)
display(pd.DataFrame(my_freq3,columns=levels))

sk_freq = sk_knn(k)
display(pd.DataFrame(sk_freq,columns=levels))

%timeit my_knn1(k)
%timeit my_knn2(k)
my_time = %timeit -o my_knn3(k)
sk_time = %timeit -o sk_knn(k)
print("\n\n")
print(sk_time.best/my_time.best)
