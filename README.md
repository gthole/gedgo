Ged-go
=====

A Gedcom viewer web app.

About
---------------
Ged-go is written in Django with d3.js visualizations and Bootstrap for mobile scaffolding, based on the idea that a genealogy website and gedcom viewer can be beautiful and intuitive.

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


Features
---------------

- Individual view
  - Easy to read podded display
  - Pedigree charts
  - Timeline of events coincided with major world historical events
- Gedcom view
- Basic search
- Blog
  - Tag people in a blog post, and those posts automatically appear in that person's individual view.
- Page for displaying documentary videos
- Email contact form
- Secure login and Admin pages
- Gedcom parser and update mechanism
- Family view
- Automatic thumbnail creation
- Responsive design for all levels of mobile browsing

 
Installation
---------------

Development installation is fairly straight-forward.  We use Vagrant and 
Virtualbox to abstract away most of the dependencies and make it easy to
get started.

Install system dependencies:
- Download and install [VirtualBox]().
- Download and install [vagrant]().
- Install [fabric]() `pip install fabric` (You may need to install [pip](), and use `sudo`.)

Now checkout the Gedgo development environment, and then Gedgo itself.

```bash
$ git clone git@github.com:gthole/gedgo_env.git
$ cd gedgo_env
$ git clone git@github.com:gthole/gedgo.git
```

Alright, let's get a virtual CentOS server running!

```bash
# Create and provision the virtual machine
$ vagrant up

# Install python dependencies, set up the MySQL db, and load with fixtures
$ fab setup_dev_env

# Start the development server
$ fab server
```

You should see two processes running, a web server and a celery worker.

Go to [localhost:8000](http://localhost:8000/), and log in with
username `devel` and password `devel`.

You can run the unit tests with a fabric command, or shell into the
machine to interact with it directly:

```bash
$ fab test
$ vagrant ssh
```

When you're done with the virtual machine and want to move on to other things,
you can shut it down with:

```bash
$ vagrant halt
```


Adding and Updating Gedcoms
---------------

```bash
$ python manage.py add_gedcom /path/to/your/file.ged
```

To update your gedcom, you can either use the manage.py command, passing it the integer ID of the gedcom object you'd like to update, for example:

```bash
$ python manage.py update_gedcom 1 /path/to/your/file.ged
```

Or, with the Celery worker running, you can use the [web interface](http://localhost:8000/gedgo/1/update).


License
---------------
Copyright (c) 2012 Gregory Thole

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
