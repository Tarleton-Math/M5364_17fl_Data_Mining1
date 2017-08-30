The main shared repo at https://github.com/Tarleton-Math/M5364_17fl_Data_Mining1.git will be public so everyone can view it.  You will create your own private repo that can sync changes from the shared.  You repo needs to be private so others can't see your homework solutions.  Here's how we do that:

Plan
- Folder "prof" common to everyone.  I will primarily manage this part to distribute course materials like homework, links, instructions, etc.  But I encourage you to add to the "prof/resources/links.md" file as you find helpful resources.
- Folder "student" is for you individually.  Nothing goes into here in the shared repo.  You will submit your hwk to your own repo in this folder for me to grade.

Instructions
1. Give me your user name
1. Confirm from link in your email to join Tarleton-Math.
1. Create new *private* repo under Tarleton-Math organization name m5364_17fl_Data_Mining_yourlastname
1. Setup your private repo to stay in sync with shared.  Instructions modified from  https://medium.com/@bilalbayasut/github-how-to-make-a-fork-of-public-repository-private-6ee8cacaf9d3
	- "shared_url" = share repo, https://github.com/Tarleton-Math/M5364_17fl_Data_Mining1.git (I'm using the word shared where the article uses public.)
	- "private_url" = URL of your personal repo (click green "clone or download button)
	1. Decide where you want stuff to live on your local hard .  Open a shell and naviagte there.  (In windows, you can right click choose "open git bash here".)
	1. git clone --bare "shared_url" (creates "temporary folder")
	1. cd into "temporary folder"
	1. git push --mirror "private_url"
	1. cd ..
	1. rm -rf "temporary folder"
	1. git clone "shared_url"
	1. git remote add shared "shared_url"
	- Hurray, you now have your private repo with a copy of the shared repo both in the cloud and on your local machine.  It has the shared repo as a "remote" called shared.

- To pull change to the shared repo:
	1. git pull origin master    (pulls all your edits to your private repo first so you don't get conflicts later)
	1. git pull shared master    (pulls all edits to the shared repo)
	1. git push origin master

git pull origin master && git pull shared master && git push origin master


- To push changes to your private repo in the cloud
	1. git pull
	1. git add *
	1. git commit -m "your commit message here"
	1. git push --all

git pull && git add * && git commit -m "your commit message here" && git push --all
