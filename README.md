Ged-go
=====

A Gedcom viewer web app.

About
---------------
Ged-go is written in Django with d3.js visualizations, based on the idea that a genealogy website and gedcom viewer can be beautiful and intuitive.

Most of the web-based genealogy software out there is pretty ugly and difficult to navigate in.  There are often silly little icons and information is presented in hard to read tables.  Instead, the philosophy of Ged-go is to have fewer features, but to present a gedcom in a clear and well designed way.

<table align=center>
  <tr><td>
    <a href="https://raw.github.com/gthole/gedgo/master/static/screenshots/individualview.png">
      <img src="https://raw.github.com/gthole/gedgo/master/static/screenshots/individualview.png" height=250 width=300>
    </a>
  </td><td>
    <a href="https://raw.github.com/gthole/gedgo/master/static/screenshots/timeline.png">
      <img src="https://raw.github.com/gthole/gedgo/master/static/screenshots/timeline.png" height=250 width=250>
    </a>
  </td></tr>
</table>


Gedgo's current features include:
* Individual view
   * Easy to read podded display
   * Pedigree charts
   * Timeline of events coincided with major world historical events
* Gedcom view
* Basic search
* Blog
   * Tag people in a blog post, and those posts automatically appear in that person's individual view.
* Page for displaying documentary videos
* Email contact form
* Secure login and Admin pages
* Gedcom parser and update mechanism
* Family view
* Automatic thumbnail creation


Ged-go is under active development.  Future features:
* Descendancy charts
* Gedcom statistics and network graph
* Advanced search
* Multiple templates



Installation / Set up
-----------
Installation is generally not for the faint of heart.  More complete instructions will follow, but the essential idea is:
* Install Django
* Install dependencies: pip install -r reqs.pip
* Include Ged-go as an installed app in your Django project, also add 'south' and 'djcelery'
* Update database with: ``python manage.py syncdb --migrate --noinput``
* Put all photos etc. into a flat file in your media directory
* Make sure your various email settings are set for the comment form
* To add a new gedcom file, use the manage.py command:

```
$ python manage.py add_gedcom /path/to/your/file.ged
```

To update your gedcom, you can either use the manage.py command, passing it the integer ID of the gedcom object you'd like to update, for example:

```
$ python manage.py update_gedcom 1 /path/to/your/file.ged
```

Or you can turn on a Celery worker server and distribute tasks to it via a web interface accessible from the "gedgo/<gedcom_id>/update" URL.


License
----------
Copyright (c) 2012 Gregory Thole

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
