SBtab - Table format for Systems Biology
========================================
Python code and example files by
<b>Timo Lubitz, Jens Hahn, Elad Noor, Frank Bergmann (2018)</b>.

Data tables in the form of spreadsheets or delimited text files are the most utilised data format in Systems Biology. However, they are often not sufficiently structured and lack clear naming conventions
that would be required for modelling. We propose the <b>SBtab</b> format as an attempt to establish an
easy-to-use table format that is both flexible and clearly structured. It comprises defined table types
for different kinds of data; syntax rules for usage of names, shortnames, and database identifiers used
for annotation; and standardised formulae for reaction stoichiometries. Predefined table types can be
used to define biochemical network models and the biochemical constants therein. The user can also
define own table types, adjusting SBtab to other types of data.

The SBtab specification can be found on the [SBtab homepage](https://www.sbtab.net/sbtab/default/specification.html).

SBtab comes along with software tools which can be employed in 3 different ways:

---

<ol>
<li><b>In the online interface</b><br>
  You can use the software tools that come with SBtab in the convenient online interface
  on https://www.sbtab.net. The page is built with the Python web framework web2py. If you want to run
  the web2py application on your own home server, you can download it from this
  repository's directory SBtab/python/web_version.
  </li>

<li><b>As a Python3 package (pip installer)</b><br>
  The tools can be employed as a Python3 package. It needs to be installed via
  pypi. Please type on your commandline<br><br>
    
  > sudo pip3 install sbtab
  
  You will then be able to import sbtab into your Python3 modules by adding
  
  > import sbtab
  
  to them. See the specification for detailed usage of this package. You will
  also find information in the repository directory SBtab/python/. **Please
  note that the directory SBtab/pypi_installer only holds the files for the
  pip installer build up and is not required at all for users that want to
  employ SBtab.**
  </li>
  
<li><b>From the command line (for experienced users)</b><br>
  You can employ the command line tools which you find in the directory
  SBtab/python. To use this option,
  you will have to install the required packages on your own and put
  the Python modules to their according directory. Details on the usage
  of the command line tools you can find in the directory SBtab/python.
</li>
</ol>

---

The SBtab repository consists of the following directories and contents:

<b>definition table:</b><br>
Default definitions of predefined SBtab table types.

<b>excel:</b><br>
windows installer and source code for the excel add-in (copyright Frank T. Bergmann).

<b>sbtab examples:</b><br>
example SBtab files.

<b>python:</b>
<ul>
<li>source scripts and command line python modules, including validator and converter to and from SBML (copyright Timo Lubitz).</li>

<li><b>documentation:</b><br>
HTML documentation of the SBtab repository and source code (copyright Timo Lubitz & Jens Hahn).</li>

<li><b>sqlite interface:</b><br>
Python interface for querying SQLite database via SBtab (copyright Elad Noor).</li>

<li><b>web2py:</b><br>
Web2py server files for the SBtab online tools. Can be run locally and offline if required (copyright Massimo Di Pierro (web2py) and Timo Lubitz (SBtab application))</li>
</ul>
