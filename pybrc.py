# Site configuration

from Pyblio.Types import *
from Pyblio import Autoload, Config

from Pyblio.TextUI import *

# ==================================================

import string, os

# define autoloaded formats

Autoload.preregister ('format', 'BibTeX',  'Pyblio.Format.BibTeX',  'file:.*\.bib')
Autoload.preregister ('format', 'RefDB',   'Pyblio.Format.RefDB',   'file:.*\.brf')
Autoload.preregister ('format', 'Ovid',    'Pyblio.Format.Ovid',    'file:.*\.ovid')
Autoload.preregister ('format', 'Medline', 'Pyblio.Format.Medline', 'file:.*\.med')
Autoload.preregister ('format', 'DocBook', 'Pyblio.Format.docbook', 'file:.*\.sgml')

# these two are very close
Autoload.preregister ('format', 'Refer',   'Pyblio.Format.Refer', 'file:.*\.refer')
Autoload.preregister ('format', 'EndNote', 'Pyblio.Format.Refer', 'file:.*\.end')


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
           'Dates', 'Institution', 'Publisher', 'Address', 'Format', 'Month',
           'Year', 'NoSeries', 'ConfPlace', 'ConfDate', 'Cote', 'IEEECN',
           'LoCN',
           'ISBN', 'ISSN', 'Note', 'Language', 'HowPublished', 'To_Appear',
           'From', 'Received', 'Owner', 'Keywords', 'Abstract', 'Remarks' ]

desc = {}
# create the hash table
for f in fields:
    desc [string.lower (f)] = FieldDescription (f)
    
# Special fields

desc ['author'].type = TypeAuthor
desc ['editor'].type = TypeAuthor

desc ['title'].type         = TypeTitle
desc ['specifictitle'].type = TypeTitle
desc ['booktitle'].type     = TypeTitle
     
desc ['year'].type     = TypeDate
desc ['confdate'].type = TypeDate


# Entry types

entries = {
    'Article' : (('author', 'title', 'journal', 'year'),
                 ('volume', 'number', 'pages', 'month', 'note')),
    
    'Book' : (('author', 'editor', 'title', 'publisher', 'year'),
              ( 'volume', 'number', 'series', 'address', 'edition',
                'month', 'note')),
    
    'Booklet' : (('title',),
                 ('author', 'howpublished', 'address', 'month', 'year',
                  'note')),
    
    'InBook' : (('author', 'editor', 'title', 'chapter', 'pages', 'publisher',
                 'year'),
                ('volume', 'number', 'series', 'type', 'address', 'edition',
                 'month', 'note')),
    
    'InCollection' : (('author', 'title', 'booktitle', 'publisher', 'year', ),
                      ('editor', 'volume', 'number', 'series', 'type',
                      'chapter', 'pages', 'address', 'edition',)),
    
    'InProceedings' : (('author', 'title', 'booktitle', 'year',),
                       ('editor', 'volume', 'number', 'series',
                       'pages', 'address', 'month', 'organization',
                       'publisher', 'note')),
    
    'Manual' : (('title',),
                ('author', 'organization', 'address', 'edition',
                'month', 'year', 'note',)),
    
    'MastersThesis' : (('author', 'title', 'school', 'year',),
                       ('type', 'address', 'month', 'note',)),
    
    'Misc' : ((),
              ('author', 'title', 'howpublished', 'month', 'year', 'note',)),
    
    'PhdThesis' : (('author', 'title', 'school', 'year',),
                       ('type', 'address', 'month', 'note',)),
    
    'Proceedings' : (('title', 'year',),
                     ('editor', 'volume', 'number', 'series',
                     'address', 'publisher', 'note', 'month',
                      'organization',)),
    
    'TechReport' : (('author', 'title', 'institution', 'year',),
                    ('type', 'number', 'address', 'month', 'note',)),
    
    'Unpublished' : (('author', 'title', 'note',),
                     ('month', 'year',)),
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

Config.set ('base/searched',
            ('Author', 'Title', 'Abstract', 'Year', 'Note',))

Config.set ('base/defaulttype', ent ['article'])


# ==================================================

from Pyblio.GnomeUI import FieldsInfo

Config.set ('gnomeui/fields', {
    'author'    : FieldsInfo.UIDescription (150, FieldsInfo.WidgetAuthor),
    'editor'    : FieldsInfo.UIDescription (150, FieldsInfo.WidgetAuthor),
    'title'     : FieldsInfo.UIDescription (200, FieldsInfo.WidgetText),
    'booktitle' : FieldsInfo.UIDescription (200, FieldsInfo.WidgetText),
    'year'      : FieldsInfo.UIDescription (50,  FieldsInfo.WidgetEntry),
    'comment'   : FieldsInfo.UIDescription (50,  FieldsInfo.WidgetText),
    'year'      : FieldsInfo.UIDescription (50,  FieldsInfo.WidgetDate),
    'confdate'  : FieldsInfo.UIDescription (50,  FieldsInfo.WidgetDate),
    })

Config.set ('gnomeui/default',
            FieldsInfo.UIDescription (150, FieldsInfo.WidgetEntry))

Config.set ('gnomeui/columns', ('Author', 'Year', 'Title'))

# ==================================================

Config.set ('endnote/table', {
    'U' : 'url',
    'A' : 'author',
    'Q' : 'author',
    'T' : 'title',
    'S' : 'series',
    'J' : 'journal',
    'B' : 'booktitle',
    'R' : 'type',
    'V' : 'volume',
    'N' : 'number',
    'E' : 'editor',
    'D' : 'year',
    'P' : 'pages',
    'I' : 'publisher',
    'C' : 'address',
    'K' : 'keywords',
    'X' : 'abstract',
    'W' : 'location',
    '0' : ' type ',
    '7' : 'edition',
    '8' : 'confdate',
    '9' : 'howpublished',
    'Y' : 'editor',
    })

Config.set ('refer/table', {
    'U' : 'url',
    'A' : 'author',
    'Q' : 'author',
    'T' : 'title',
    'S' : 'series',
    'J' : 'journal',
    'B' : 'booktitle',
    'R' : 'type',
    'V' : 'volume',
    'N' : 'number',
    'E' : 'editor',
    'D' : 'year',
    'P' : 'pages',
    'I' : 'publisher',
    'C' : 'address',
    'K' : 'keywords',
    'X' : 'abstract',
    'W' : 'location',
    })

Config.set ('endnote/types', {
    'Artwork' : 'misc',
    'Audiovisual Material' : 'misc',
    'Book' : 'book',
    'Book Section' : 'inbook',
    'Computer Program' : 'manual',
    'Conference Proceedings' : 'proceedings',
    'Edited Book' : 'book',
    'Generic' : 'misc',
    'Journal Article' : 'article',
    'Magazine Article' : 'article',
    'Map' : 'misc',
    'Newspaper Article' : 'article',
    'Patent' : 'misc',
    'Personal Communication' : 'misc',
    'Report' : 'techreport',
    'Thesis' : 'phdthesis',
    })

    
