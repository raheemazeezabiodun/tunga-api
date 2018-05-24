# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import tagulous.models
from django.db import models

from tunga_utils.constants import SKILL_TYPE_CHOICES, SKILL_TYPE_OTHER


class Skill(tagulous.models.TagModel):
    type = models.CharField(
        max_length=30, choices=SKILL_TYPE_CHOICES, default=SKILL_TYPE_OTHER,
        help_text=','.join(['%s - %s' % (item[0], item[1]) for item in SKILL_TYPE_CHOICES])
    )

    class TagMeta:
        initial = "PHP, JavaScript, Python, Ruby, Java, C#, C++, Ruby, Swift, Objective C, .NET, ASP.NET, Node.js," \
                  "HTML, CSS, HTML5, CSS3, XML, JSON, YAML," \
                  "Django, Ruby on Rails, Flask, Yii, Lavarel, Express.js, Spring, JAX-RS," \
                  "AngularJS, React.js, Meteor.js, Ember.js, Backbone.js," \
                  "WordPress, Joomla, Drupal," \
                  "jQuery, jQuery UI, Bootstrap, AJAX," \
                  "Android, iOS, Windows Mobile, Apache Cordova, Ionic," \
                  "SQL, MySQL, PostgreSQL, MongoDB, CouchDB," \
                  "Git, Subversion, Mercurial, " \
                  "Docker, Ansible, " \
                  "Webpack, Grunt, Gulp, Ant, Maven, Gradle"
        space_delimiter = False
