My GitHub repo will be public so everyone can view it.  But your clone needs to be private so others can't see your homework solutions.  Here's how we do that:

- Give me your user name
- Confirm from link in your email to join Tarleton-Math.
- Create new *private* repo under Tarleton-Math organization name m5364_17fl_Data_Mining_yourlastname
- Setup your repo to stay in sync with the share.  Instructions modified from  https://medium.com/@bilalbayasut/github-how-to-make-a-fork-of-public-repository-private-6ee8cacaf9d3

-- "shared_url" = share repo, https://github.com/Tarleton-Math/M5364_17fl_Data_Mining1.git (I'm using the word shared where the article uses public.)

-- "private_url" = your personal repo (click green "clone or download button)

-- Determine where on your local hard you want stuff to live.  Open a shell and naviagte.  (In windows, you can right click choose "open git bash here".)
-- git clone --bare "shared_url" (creates temporary folder)
-- cd into the dir it just made
-- git push --mirror "private_url"
-- cd ..
-- rm -rf "temporary folder"
-- git clone "shared_url"
-- git remote add shared "shared_url"
-- Hurray, you now have your private copy of the shared repo both in the cloud and on your local machine.  It has the shared repo as a "remote" called shared.  If you don't like its location, you should be able to move it by simply cutting everything and pasting into the desired location.

- To pull change mades to the shared repo:
-- Navigate to directory.  Open git bash.
-- git pull origin master    (pulls all your edits to your private repo first so you don't get conflicts later)
-- git pull shared master    (pulls all edits to the shared repo)
-- git push origin master

git pull origin master && git pull shared master && git push origin master


- To push change to your private repo in the cloud
-- git pull
-- git add *
-- git commit -m "your commit message here"
-- git push --all

git pull && git add * && git commit -m "your commit message here" && git push --all
