# Description

`campus-dl` is a simple tool to download videos and lecture materials from [campus](https://campus.gov.il/).    
It requires a [Python][python] interpreter (>= 3.8) and
very few other dependencies.  


# Installation (recommended)

To install campus-dl run:

    pip install git+https://github.com/imvladikon/campus-dl

# Manual Installation

To install all the dependencies please do:

    pip install -r requirements.txt

## youtube-dl

One of the most important dependencies of `campus-dl` is `yt-dlp`. The
installation step listed above already pulls in the most recent version of
`yt-dlp` for you.

Unfortunately, since many Open edX sites store their videos on Youtube and
Youtube changes their layout from time to time, it may be necessary to
upgrade your copy of `yt-dlp`.  There are many ways to proceed here, but
the simplest is to simply use:

    pip install --upgrade yt-dlp

# Quick Start

#### Example of usage

```bash
campus-dl -u  user@user.com -p <PASSWORD> -s https://courses.campus.gov.il/courses/course-v1:CS+GOV_CS_Data_DataIntro101_HE+2022_2/course/
```

#### Command line

Once you have installed everything, to use `campus-dl.py`, let it discover the
courses in which you are enrolled, by issuing:

    campus-dl -u user@user.com --list-courses

From there, choose the course you are interested in, copy its URL and use it
in the following command:

    campus-dl -u user@user.com COURSE_URL

replacing `COURSE_URL` with the URL that you just copied in the first step.
It should look something like:
https://courses.campus.gov.il/courses/course-v1:CS+GOV_CS_Data_DataIntro101_HE+2022_2/course/

Your downloaded videos will be placed in a new directory called
`Downloaded`, inside your current directory, but you can also choose another
destination with the `-o` argument.

To see all available options and a brief description of what they do, simply
execute:

    campus-dl --help




