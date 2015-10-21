# Creating a Local Copy of the Code #

First you need to create a local copy of the repository, you can `checkout` the repo with the following command (available from the `source` tab of our project):

```
svn checkout https://website-clustering.googlecode.com/svn/trunk/ <ProjectFolderName> --username <UserName>
```

that's all one line, e.g. I wrote:

```
svn checkout https://website-clustering.googlecode.com/svn/trunk/ website-clustering --username ma.faucher
```

# Main commands #

Now you have a local copy in `<ProjectFolderName>`, so all the following commands are run from inside this folder.

The usual workflow is like this, first you want to update your repo to make sure you have the latest code, just run:

```
svn update
```

If you just want to make changes to _existing_ files, those changes will be tracked by svn. Just make the changes and commit your changes by using:

```
svn commit -m "Description of changes"
```

Remember that svn is only aware of the files currently in the repository. If you need to create a new directory use:

```
svn mkdir <DirectoryName>
```

To add a new file use:

```
svn add <FileName>
```

To remove a file use:

```
svn remove <FileName>
```

You can also check the status of your local copy of the repository with:

```
svn status
```

This will list info about how your copy differs from the central
repository, here's a quick legend:

  * `?` File was added, but no changes were tracked (you didn't run `svn add filename`)

  * `!` File was deleted, but no changes were tracked (you didn't run `svn remove <filename>`)

  * `A` File will be added next time you commit

  * `D` File will be deleted next time you commit

  * `U` File will be updated next time you commit

There are some other possible messages, but I'll update this as I see them

# Conflicts & Correcting mistakes #

The problems mainly occur when you get a conflict. When you try to commit a file while you were not working on the latest version (or someone changed the file while you were editing it). If you try to commit, svn will inform you of the file(s) which cause a conflict, and give you a series of options. The main two options I use is "accept mine", which takes your changes, but not those that were committed by the other user, and "accept theirs" which forgets about the changes you just made and keeps the file presently in the repo. There are also options to ignore until the next commit, or see a line-by-line comparison of the conflict.

That's mainly what you need to know on a daily basis... but here are some more commands.

If you make changes to a file and realize you made a mistake, you can `revert` this file back to the one in the repo:

```
svn revert <filename>
```

Now if you made a major mistake, and screwed up the whole repo, there is a way to roll-back to an old version of the repo. Let's say we are at version 56, and we want to go back to version 55:

```
svn merge --dry-run -r 56:55 https://website-clustering.googlecode.com/svn/trunk/
svn merge -r 56:55 https://website-clustering.googlecode.com/svn/trunk/
svn commit -m "Reverted to revision 55."
```

The `dry-run` allows you to see what would be rolled-back without actually doing anything. Alternatively you can use the `diff` command to see the difference between two versions:

```
svn diff -r 56:55 https://website-clustering.googlecode.com/svn/trunk/
```