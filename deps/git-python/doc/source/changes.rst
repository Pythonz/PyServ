=========
Changelog
=========

NEXT
====
* Blob Type
 * Added mode constants to ease the manual creation of blobs

0.3.1 Beta 2
============
* Added **reflog support** ( reading and writing )

 * New types: ``RefLog`` and ``RefLogEntry``
 * Reflog is maintained automatically when creating references and deleting them
 * Non-intrusive changes to ``SymbolicReference``, these don't require your code to change. They allow to append messages to the reflog.
 
     * ``abspath`` property added, similar to ``abspath`` of Object instances
     * ``log()`` method added
     * ``log_append(...)`` method added
     * ``set_reference(...)`` method added (reflog support)
     * ``set_commit(...)`` method added (reflog support)
     * ``set_object(...)`` method added (reflog support)

 * **Intrusive Changes** to ``Head`` type
 
  * ``create(...)`` method now supports the reflog, but will not raise ``GitCommandError`` anymore as it is a pure python implementation now. Instead, it raises ``OSError``.
  
 * **Intrusive Changes** to ``Repo`` type
 
  * ``create_head(...)`` method does not support kwargs anymore, instead it supports a logmsg parameter
     
* Repo.rev_parse now supports the [ref]@{n} syntax, where *n* is the number of steps to look into the reference's past

* **BugFixes**

    * Removed incorrect ORIG_HEAD handling
 
* **Flattened directory** structure to make development more convenient.

 * .. note:: This alters the way projects using git-python as a submodule have to adjust their sys.path to be able to import git-python successfully.
 * Misc smaller changes and bugfixes

0.3.1 Beta 1
============
* Full Submodule-Support
* Added unicode support for author names. Commit.author.name is now unicode instead of string.
* Head Type changes

 * config_reader() & config_writer() methods added for access to head specific options.
 * tracking_branch() & set_tracking_branch() methods addded for easy configuration of tracking branches.


0.3.0 Beta 2
============
* Added python 2.4 support

0.3.0 Beta 1
============
Renamed Modules
---------------
* For consistency with naming conventions used in sub-modules like gitdb, the following modules have been renamed

  * git.utils -> git.util
  * git.errors -> git.exc
  * git.objects.utils -> git.objects.util
  
General
-------
* Object instances, and everything derived from it, now use binary sha's internally. The 'sha' member was removed, in favor of the 'binsha' member. An 'hexsha' property is available for convenient conversions. They may only be initialized using their binary shas, reference names or revision specs are not allowed anymore.
* IndexEntry instances contained in IndexFile.entries now use binary sha's. Use the .hexsha property to obtain the hexadecimal version. The .sha property was removed to make the use of the respective sha more explicit.
* If objects are instantiated explicitly, a binary sha is required to identify the object, where previously any rev-spec could be used. The ref-spec compatible version still exists as Object.new or Repo.commit|Repo.tree respectively.
* The .data attribute was removed from the Object type, to obtain plain data, use the data_stream property instead.
* ConcurrentWriteOperation was removed, and replaced by LockedFD
* IndexFile.get_entries_key was renamed to entry_key
* IndexFile.write_tree: removed missing_ok keyword, its always True now. Instead of raising GitCommandError it raises UnmergedEntriesError. This is required as the pure-python implementation doesn't support the missing_ok keyword yet.
* diff.Diff.null_hex_sha renamed to NULL_HEX_SHA, to be conforming with the naming in the Object base class
 

0.2 Beta 2
===========
 * Commit objects now carry the 'encoding' information of their message. It wasn't parsed previously, and defaults to UTF-8
 * Commit.create_from_tree now uses a pure-python implementation, mimicing git-commit-tree

0.2
=====
General
-------
* file mode in Tree, Blob and Diff objects now is an int compatible to definintiions 
  in the stat module, allowing you to query whether individual user, group and other 
  read, write and execute bits are set.
* Adjusted class hierarchy to generally allow comparison and hash for Objects and Refs
* Improved Tag object which now is a Ref that may contain a tag object with additional 
  Information
* id_abbrev method has been removed as it could not assure the returned short SHA's 
  where unique
* removed basename method from Objects with path's as it replicated features of os.path
* from_string and list_from_string methods are now private and were renamed to 
  _from_string  and _list_from_string respectively. As part of the private API, they 
  may change without prior notice.
* Renamed all find_all methods to list_items - this method is part of the Iterable interface
  that also provides a more efficients and more responsive iter_items method
* All dates, like authored_date and committer_date, are stored as seconds since epoc
  to consume less memory - they can be converted using time.gmtime in a more suitable 
  presentation format if needed.
* Named method parameters changed on a wide scale to unify their use. Now git specific 
  terms are used everywhere, such as "Reference" ( ref ) and "Revision" ( rev ).
  Prevously multiple terms where used making it harder to know which type was allowed
  or not.
* Unified diff interface to allow easy diffing between trees, trees and index, trees
  and working tree, index and working tree, trees and index. This closely follows
  the git-diff capabilities.
* Git.execute does not take the with_raw_output option anymore. It was not used 
  by anyone within the project and False by default.
  

Item Iteration
--------------
* Previously one would return and process multiple items as list only which can 
  hurt performance and memory consumption and reduce response times. 
  iter_items method provide an iterator that will return items on demand as parsed 
  from a stream. This way any amount of objects can be handled.
* list_items method returns IterableList allowing to access list members by name
  
objects Package
----------------
* blob, tree, tag and commit module have been moved to new objects package. This should 
  not affect you though unless you explicitly imported individual objects. If you just 
  used the git package, names did not change.
  
Blob
----
* former 'name' member renamed to path as it suits the actual data better

GitCommand
-----------
* git.subcommand call scheme now prunes out None from the argument list, allowing 
  to be called more confortably as None can never be a valid to the git command 
  if converted to a string.
* Renamed 'git_dir' attribute to 'working_dir' which is exactly how it is used

Commit
------
* 'count' method is not an instance method to increase its ease of use
* 'name_rev' property returns a nice name for the commit's sha

Config
------
* The git configuration can now be read and manipulated directly from within python
  using the GitConfigParser
* Repo.config_reader() returns a read-only parser
* Repo.config_writer() returns a read-write parser 
 
Diff
----
* Members a a_commit and b_commit renamed to a_blob and b_blob - they are populated
  with Blob objects if possible
* Members a_path and b_path removed as this information is kept in the blobs
* Diffs are now returned as DiffIndex allowing to more quickly find the kind of 
  diffs you are interested in
  
Diffing
-------
* Commit and Tree objects now support diffing natively with a common interface to 
  compare agains other Commits or Trees, against the working tree or against the index.

Index
-----
* A new Index class allows to read and write index files directly, and to perform
  simple two and three way merges based on an arbitrary index.
  
Referernces
------------
* References are object that point to a Commit
* SymbolicReference are a pointer to a Reference Object, which itself points to a specific
  Commit
* They will dynmically retrieve their object at the time of query to assure the information 
  is actual. Recently objects would be cached, hence ref object not be safely kept 
  persistent.
  
Repo
----
* Moved blame method from Blob to repo as it appeared to belong there much more.
* active_branch method now returns a Head object instead of a string with the name 
  of the active branch.
* tree method now requires a Ref instance as input and defaults to the active_branche
  instead of master
* is_dirty now takes additional arguments allowing fine-grained control about what is 
  considered dirty
* Removed the following methods:

  - 'log' method as it as effectively the same as the 'commits' method
  - 'commits_since' as it is just a flag given to rev-list in Commit.iter_items
  - 'commit_count' as it was just a redirection to the respective commit method
  - 'commits_between', replaced by a note on the iter_commits method as it can achieve the same thing
  - 'commit_delta_from' as it was a very special case by comparing two different repjrelated repositories, i.e. clones, git-rev-list would be sufficient to find commits that would need to be transferred for example.
  - 'create' method which equals the 'init' method's functionality
  - 'diff' - it returned a mere string which still had to be parsed
  - 'commit_diff' - moved to Commit, Tree and Diff types respectively
  
* Renamed the following methods:

  - commits to iter_commits to improve the performance, adjusted signature
  - init_bare to init, implying less about the options to be used
  - fork_bare to clone, as it was to represent general clone functionality, but implied
    a bare clone to be more versatile
  - archive_tar_gz and archive_tar and replaced by archive method with different signature
  
* 'commits' method has no max-count of returned commits anymore, it now behaves  like git-rev-list
* The following methods and properties were added

  - 'untracked_files' property, returning all currently untracked files
  - 'head', creates a head object
  - 'tag', creates a tag object
  - 'iter_trees' method
  - 'config_reader' method
  - 'config_writer' method
  - 'bare' property, previously it was a simple attribute that could be written
  
* Renamed the following attributes

  - 'path' is now 'git_dir'
  - 'wd' is now 'working_dir'
  
* Added attribute

  - 'working_tree_dir' which may be None in case of bare repositories
  
Remote
------
* Added Remote object allowing easy access to remotes
* Repo.remotes lists all remotes
* Repo.remote returns a remote of the specified name if it exists

Test Framework
--------------
* Added support for common TestCase base class that provides additional functionality
  to receive repositories tests can also write to. This way, more aspects can be 
  tested under real-world ( un-mocked ) conditions.

Tree
----
* former 'name' member renamed to path as it suits the actual data better
* added traverse method allowing to recursively traverse tree items
* deleted blob method
* added blobs and trees properties allowing to query the respective items in the 
  tree
* now mimics behaviour of a read-only list instead of a dict to maintain order.
* content_from_string method is now private and not part of the public API anymore


0.1.6
=====

General
-------
* Added in Sphinx documentation.

* Removed ambiguity between paths and treeishs. When calling commands that
  accept treeish and path arguments and there is a path with the same name as
  a treeish git cowardly refuses to pick one and asks for the command to use
  the unambiguous syntax where '--' seperates the treeish from the paths.

* ``Repo.commits``, ``Repo.commits_between``, ``Reop.commits_since``,
  ``Repo.commit_count``, ``Repo.commit``, ``Commit.count`` and
  ``Commit.find_all`` all now optionally take a path argument which
  constrains the lookup by path.  This changes the order of the positional
  arguments in ``Repo.commits`` and ``Repo.commits_since``.

Commit
------
* ``Commit.message`` now contains the full commit message (rather than just
  the first line) and a new property ``Commit.summary`` contains the first
  line of the commit message.

* Fixed a failure when trying to lookup the stats of a parentless commit from
  a bare repo.

Diff
----
* The diff parser is now far faster and also addresses a bug where
  sometimes b_mode was not set.

* Added support for parsing rename info to the diff parser. Addition of new
  properties ``Diff.renamed``, ``Diff.rename_from``, and ``Diff.rename_to``.

Head
----
* Corrected problem where branches was only returning the last path component
  instead of the entire path component following refs/heads/.

Repo
----
* Modified the gzip archive creation to use the python gzip module.

* Corrected ``commits_between`` always returning None instead of the reversed
  list.


0.1.5
=====

General
-------
* upgraded to Mock 0.4 dependency.

* Replace GitPython with git in repr() outputs.

* Fixed packaging issue caused by ez_setup.py.

Blob
----
* No longer strip newlines from Blob data.

Commit
------
* Corrected problem with git-rev-list --bisect-all. See
  http://groups.google.com/group/git-python/browse_thread/thread/aed1d5c4b31d5027

Repo
----
* Corrected problems with creating bare repositories.

* Repo.tree no longer accepts a path argument. Use:

    >>> dict(k, o for k, o in tree.items() if k in paths)

* Made daemon export a property of Repo. Now you can do this:

    >>> exported = repo.daemon_export
    >>> repo.daemon_export = True

* Allows modifying the project description. Do this:

    >>> repo.description = "Foo Bar"
    >>> repo.description
    'Foo Bar'

* Added a read-only property Repo.is_dirty which reflects the status of the
  working directory.

* Added a read-only Repo.active_branch property which returns the name of the
  currently active branch.


Tree
----
* Switched to using a dictionary for Tree contents since you will usually want
  to access them by name and order is unimportant.

* Implemented a dictionary protocol for Tree objects. The following:

    child = tree.contents['grit']

  becomes:

    child = tree['grit']

* Made Tree.content_from_string a static method.

0.1.4.1
=======

* removed ``method_missing`` stuff and replaced with a ``__getattr__``
  override in ``Git``.

0.1.4
=====

* renamed ``git_python`` to ``git``. Be sure to delete all pyc files before
  testing.

Commit
------
* Fixed problem with commit stats not working under all conditions.

Git
---
* Renamed module to cmd.

* Removed shell escaping completely.

* Added support for ``stderr``, ``stdin``, and ``with_status``.

* ``git_dir`` is now optional in the constructor for ``git.Git``.  Git now 
  falls back to ``os.getcwd()`` when git_dir is not specified.

* add a ``with_exceptions`` keyword argument to git commands. 
  ``GitCommandError`` is raised when the exit status is non-zero.

* add support for a ``GIT_PYTHON_TRACE`` environment variable. 
  ``GIT_PYTHON_TRACE`` allows us to debug GitPython's usage of git through 
  the use of an environment variable.

Tree
----
* Fixed up problem where ``name`` doesn't exist on root of tree.

Repo
----
* Corrected problem with creating bare repo.  Added ``Repo.create`` alias.

0.1.2
=====

Tree
----
* Corrected problem with ``Tree.__div__`` not working with zero length files.  
  Removed ``__len__`` override and replaced with size instead. Also made size 
  cach properly. This is a breaking change.

0.1.1
=====
Fixed up some urls because I'm a moron

0.1.0
=====
initial release
