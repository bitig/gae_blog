# GAE blog

## What is it
gae_blog is a blog platform written written for the Google App Engine environment. It is created as part of the full-stack nanodegree from Udacity.

## Install and Run
Install Python 2.7 and the [Python App Engine Standard Environment](https://cloud.google.com/appengine/docs/python/quickstart) to your local machine.
  1. `git clone https://github.com/jdiii/gae_blog.git` to your local machine
  2. `cd` to the gae_blog folder
  3. run the application with the command `dev_appserver.py app.yaml`
The app will now be running at http://localhost:8080/blog/


## Features
Users can create an account, create posts, and like posts by other users. Logged in users can delete and edit their own posts.

## Tech
Written in Python using the GAE APIs. Templating via Jinga2. Front-end relies heavily on Bootstrap. Password hashing relies on BCrypt.
