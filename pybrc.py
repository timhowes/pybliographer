# Site configuration

from Pyblio.Types  import *
from Pyblio.Fields import *

from Pyblio import Autoload, Config

from Pyblio.TextUI import *

# ==================================================

import string, os

# define autoloaded formats

Autoload.preregister ('format', 'BibTeX',  'Pyblio.Format.BibTeX',  '.*\.bib')
Autoload.preregister ('format', 'Ovid',    'Pyblio.Format.Ovid',    '.*\.ovid')
Autoload.preregister ('format', 'Medline', 'Pyblio.Format.Medline', '.*\.med')
Autoload.preregister ('format', 'Refer',   'Pyblio.Format.Refer',   '.*\.refer')


# define styles and outputs

Autoload.preregister ('style', 'Alpha',  'Pyblio.Style.alpha')
Autoload.preregister ('style', 'Abbrv',  'Pyblio.Style.alpha')
Autoload.preregister ('style', 'Custom', 'Pyblio.Style.custom')

Autoload.preregister ('output', 'Text',  'Pyblio.Output.text')
Autoload.preregister ('output', 'Raw',   'Pyblio.Output.raw')
Autoload.preregister ('output', 'HTML',  'Pyblio.Output.html')
Autoload.preregister ('output', 'LaTeX', 'Pyblio.Output.LaTeX')


# Parse the configuration directory

rootconfig = os.path.join ('Pyblio', 'ConfDir')

if not os.path.isdir (rootconfig):
    rootconfig = os.path.join (pyb_prefix, 'Pyblio', 'ConfDir')
    
if os.path.isdir (rootconfig):
    Config.parse_directory (rootconfig)


# ==================================================

# Available fields

fields = [ 'CrossRef', 'Key', 'Author', 'Address_1', 'Address_2',
           'Title', 'SpecificTitle', 'Journal', 'Special', 'Type', 'BookTitle',
           'Subject', 'Ownership', 'Series', 'Editor', 'Edition', 'Volume',
           'Number', 'Chapter', 'Pages', 'School', 'Organization', 'Location',
           'Dates', 'Institution', 'Publisher', 'Address', 'Format',
           'PubDate', 'Date', 'NoSeries', 'ConfPlace', 'ConfDate', 'Cote', 'IEEECN',
           'LoCN', 'ISBN', 'ISSN', 'Note', 'Language', 'HowPublished', 'To_Appear',
           'From', 'Received', 'Owner', 'Keywords', 'Abstract', 'Remarks', 'URL' ]

desc = {}
# create the hash table
for f in fields:
    desc [string.lower (f)] = FieldDescription (f)
    
# Special fields

desc ['author'].type = AuthorGroup.id
desc ['editor'].type = AuthorGroup.id

desc ['pubdate'].type  = Date.id
desc ['confdate'].type = Date.id

desc ['crossref'].type = Reference.id

desc ['url'].type      = URL.id


# Entry types

entries = {
    'Article' : (('author', 'title', 'journal', 'pubdate'),
                 ('volume', 'number', 'pages', 'note')),
    
    'Book' : (('author', 'editor', 'title', 'publisher', 'pubdate'),
              ( 'volume', 'number', 'series', 'address', 'edition',
                'note')),
    
    'Booklet' : (('title',),
                 ('author', 'howpublished', 'address', 'pubdate',
                  'note')),
    
    'InBook' : (('author', 'editor', 'title', 'chapter', 'pages', 'publisher',
                 'pubdate'),
                ('volume', 'number', 'series', 'type', 'address', 'edition',
                  'note')),
    
    'InCollection' : (('author', 'title', 'booktitle', 'publisher', 'pubdate', ),
                      ('editor', 'volume', 'number', 'series', 'type',
                      'chapter', 'pages', 'address', 'edition',)),
    
    'InProceedings' : (('author', 'title', 'booktitle', 'pubdate',),
                       ('editor', 'volume', 'number', 'series',
                       'pages', 'address', 'organization',
                       'publisher', 'note')),
    
    'Manual' : (('title',),
                ('author', 'organization', 'address', 'edition',
                 'pubdate', 'note',)),
    
    'MastersThesis' : (('author', 'title', 'school', 'pubdate',),
                       ('type', 'address', 'note',)),
    
    'Misc' : ((),
              ('author', 'title', 'howpublished', 'pubdate', 'note',)),
    
    'PhdThesis' : (('author', 'title', 'school', 'pubdate',),
                       ('type', 'address', 'note',)),
    
    'Proceedings' : (('title', 'pubdate',),
                     ('editor', 'volume', 'number', 'series',
                     'address', 'publisher', 'note',
                      'organization',)),
    
    'TechReport' : (('author', 'title', 'institution', 'pubdate',),
                    ('type', 'number', 'address', 'note',)),
    
    'Unpublished' : (('author', 'title', 'note',),
                     ('date',)),
    }

ent = {}
for e in entries.keys ():
    d = EntryDescription (e)

    d.mandatory = \
        map (lambda x, desc=desc: desc [x], entries [e] [0])
    d.optional  = \
        map (lambda x, desc=desc: desc [x], entries [e] [1])

    ent [string.lower (e)] = d


Config.set ('base/fields', desc)
Config.set ('base/entries', ent)
Config.set ('base/defaulttype', ent ['article'])


# ==================================================

from Pyblio.GnomeUI import FieldsInfo

Config.set ('gnomeui/fields', {
    'author'    : FieldsInfo.UIDescription (150, FieldsInfo.WidgetAuthor),
    'editor'    : FieldsInfo.UIDescription (150, FieldsInfo.WidgetAuthor),
    'title'     : FieldsInfo.UIDescription (200, FieldsInfo.WidgetText),
    'booktitle' : FieldsInfo.UIDescription (200, FieldsInfo.WidgetText),
    'comment'   : FieldsInfo.UIDescription (50,  FieldsInfo.WidgetText),
    'date'      : FieldsInfo.UIDescription (50,  FieldsInfo.WidgetDate),
    'pubdate'   : FieldsInfo.UIDescription (50,  FieldsInfo.WidgetDate),
    'confdate'  : FieldsInfo.UIDescription (50,  FieldsInfo.WidgetDate),
    })

Config.set ('gnomeui/default',
            FieldsInfo.UIDescription (150, FieldsInfo.WidgetEntry))

Config.set ('gnomeui/columns', ('Author', 'Date', 'Title'))


    
