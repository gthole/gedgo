Ged-go
=====

A Gedcom viewer web app.

About
---------------
Ged-go is written in Django with d3.js visualizations, based on the idea that a genealogy website and gedcom viewer can be beautiful and intuitive.

Most of the web-based genealogy software out there is pretty ugly and difficult to navigate in.  There are often silly little icons and information is presented in hard to read tables.  Instead, the philosophy of Ged-go is to have fewer features, but to present a gedcom in a clear and well designed way.

Gedgo's current features include:
* Individual view
   * Easy to read podded display
   * Timeline of events coincided with major world historical events
* Gedcom view
* Basic search
* Blog
   * Tag people in a blog post, and those posts automatically appear in that person's individual view.
* Page for displaying documentary videos
* Email contact form
* Secure login and Admin pages
* Gedcom parser and update mechanism

Ged-go is under active development.  Future features:
* Family view
* Pedigree charts
* Gedcom statistics and network graph
* Advanced search
* Multiple templates
 
 
 
Installation / Set up
-----------
Installation is generally not for the faint of heart.  More complete instructions will follow, but the essential idea is:
* Install Django
* Include Ged-go as an installed app in your Django project
* Put all photos etc. into a flat file in your media directory
* Make sure your various email settings are set for the comment form
* To parse and read in your gedcom file, from the manage.py shell:

```python
>>> from gedgo.update import update
>>> update(None, 'mygedcomfile.ged')
```
