# DelphiScriptFormatter

A Formatter Using [Quadroids Binaries](https://github.com/quadroid/jcf-pascal-format/releases/tag/v1.0.1) that also supports DelphiScript and Code Snippets

Formatting Altium Delphi Script Code is not trivial. The problem is that tools like
[JEDI Code Format](https://jedicodeformat.sourceforge.net/)
and the newer CLI version
[JCF pascal Format](https://github.com/quadroid/jcf-pascal-format)
refuse to format DelphiScript Code because it is "not complete".

Here is a little Python program that:

* Completes your DelphiScript code by inserting "unit Test;" + "interface" + "implementation" at the beginning and "end." at the end
* Formats the Result with Quadroids CLI Formatter
* Removes the formerly added elements from the result and writes the formatted code back
* A backup of your code will be generated (.bak)

<img src="doc/Prog.PNG" title="" alt="Program" width="400">

Usage:

* Get the latest release from [HERE](https://github.com/dotmjsc/DelphiScriptFormatter/releases/)
* Extract everything to a folder and run "FormatDS.exe"
* Open your DelphiScript file with "Open"
* Optionally load a different Config File (than the pascal-format.cfg in the folder)
* Click on "Process" to Format your file
* Function declaration comma Handling:
  * If this box is checked, it will replace all commas in function and procedure declarations with semicolons so that JCF can handle it
  * If "Change declaration delimiters to semicolons" is set then the declaration delimiters will stay semicolons, else they will be changed back to commas after formatting
* Preprocess 'like' statement: check this box to preprocess the like statement so that JCF can format the code

<u>Config File:</u>
Optionally, you can load your own Config File. Config files made with the GUI of the old [JEDI Code Format](https://jedicodeformat.sourceforge.net/) are automatically detected and converted.



<u>Processing of like statements:</u>

Optionally, the unsupported like statements are preprocessed so that JCF can handle the file. For this a non-comment line or the non comment part of a line like this

```
if (a=b) and (a like c) and not (c = e) and (e like f)  and (u = i)   and (u = i)  and (a like c) then  // test something like nothing
```

will be analysed, then the like statements will be each bereplaced by a '='. A comment line will be added above that has restoring info:

```
// LIKEPROCESSING_INFO: 1,3,6
if (a=b) and (a = c) and not (c = e) and (e = f)  and (u = i)   and (u = i)  and (a = c) then  // test something like nothing
```

After formatting with JCF, the tool searches for these comments and restores the 'like' statements to their original positions. finally, the like processing comments are removed from the formatted code.
