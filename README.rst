Schedule Convert
================

Use this to convert any schedule to a frab-compatible XML.

Installation
------------

It's simple::

    pip install schedule-convert

Usage
-----

Run it like this::

    schedule_convert input1.xml input2.json -o schedule.xml

Formats of the source files are detected automatically. The target format
can be specified with a ``-f`` argument. Possible values are:

* ``xml``: Frab xml.
* ``ical``: iCalendar-compatible ics file.
* ``xcal``: xCal file, not sure what for.

Input Formats
-------------

* Frab XML. Obviously.
* Sessionize JSON. See `this page`_ to enable it for your conference, or send
  the link to the person who has the rights.
* Ini-file. Put it first to set the conference's properties. Possible keys are:

  - *title* (required)
  - *slug* (required)
  - *url* (required)
  - *timezone*: only simple ``+05`` or ``-11`` are supported.
  - *track*: the default track name for events.

* CSV table. Must have a header with column names. Supported columns are:

  - *day*: format is ``YYYY-MM-DD`` or simpler ``MM-DD``. You only need to write it
    once per day.
  - *room*: again, write it once at the top of the room schedule.
  - *track*: event track. If empty, using the first non-empty value above this row.
  - *title*: required.
  - *start*: start time, as ``HH:MM``.
  - *end*: end time, as ``HH:MM``. Optional if this is not the last event in the
    room this day, or if there is a *duration*.
  - *duration*: duration of the event in minutes. Again, use either this column
    or *end*. You need to have one.
  - *speaker* or *speakers*: list them separated with commas or semicolons.
  - *abstract*, *description*, *subtitle*, *url*, *language*, *id*: optional
    fields of the event.

.. _this page: https://sessionize.com/api-documentation#question_3

Landing Page
------------

The schedule converter has an option to generate a whole directory worth
of files along with an HTML to present to attendees::

    schedule_convert input1.xml input2.json -l output https://conf.info/schedule

With that, it will generate these files in the ``output`` directory:

* ``schedule.xml`` with the frab-compatible XML schedule.
* ``schedule.ics`` with the iCalendar-compatible schedule.
* ``schedule.xml.png`` and ``schedule.ics.png`` with QR codes for the URLs to
  the above schedules. It will use the given base path: ``https://conf.info/schedule.xml``.
* ``giggity.png`` with a QR code for the Giggity app.
* ``schedule.html`` with the landing page linking to all of these files.

After making these, upload the files to your web server and share the link
with the conference attendees.

Author and License
------------------

Written by Ilya Zverev, published under MIT license.
