from Pyblio import Config, Types, Fields

Config.define ('base/fields', """ Existing fields.  It's a hash table,
               with the field name (lower case) as key, and a instance
               of Types.FieldDescription as value. """)


Config.define ('base/entries', """ Existing entries.  It's a hash
               table, with the entry name (lower case) as key, and a
               instance of Types.EntryDescription as value. """)

Config.define ('base/defaulttype', """ Default type for a newly created entry """)

Config.define ('base/lyxpipe', """ Path to the LyX server """)

# --------------------------------------------------

Config.set ('base/lyxpipe', '~/.lyx/lyxpipe')

# Available fields

fields = [ 'CrossRef', 'Key', 'Author', 'Address_1', 'Address_2',
           'Title', 'SpecificTitle', 'Journal', 'Special', 'Type', 'BookTitle',
           'Subject', 'Ownership', 'Series', 'Editor', 'Edition', 'Volume',
           'Number', 'Chapter', 'Pages', 'School', 'Organization', 'Location',
           'Dates', 'Institution', 'Publisher', 'Address', 'Format',
           'Date', 'NoSeries', 'ConfPlace', 'Cote', 'IEEECN',
           'LoCN', 'ISBN', 'ISSN', 'Note', 'Language', 'HowPublished', 'To_Appear',
           'From', 'Received', 'Owner', 'Keywords', 'Abstract', 'Remarks', 'URL' ]

desc = {}
# create the hash table
for f in fields:
    desc [string.lower (f)] = Types.FieldDescription (f)
    
# Special fields

desc ['author'].type = Fields.AuthorGroup
desc ['editor'].type = Fields.AuthorGroup

desc ['date'].type  = Fields.Date

desc ['crossref'].type = Fields.Reference

desc ['url'].type      = Fields.URL


# Entry types

entries = {
    'Article' : (('author', 'title', 'journal', 'date'),
                 ('volume', 'number', 'pages', 'note')),
    
    'Book' : (('author', 'editor', 'title', 'publisher', 'date'),
              ( 'volume', 'number', 'series', 'address', 'edition',
                'note')),
    
    'Booklet' : (('title',),
                 ('author', 'howpublished', 'address', 'date',
                  'note')),
    
    'InBook' : (('author', 'editor', 'title', 'chapter', 'pages', 'publisher',
                 'date'),
                ('volume', 'number', 'series', 'type', 'address', 'edition',
                  'note')),
    
    'InCollection' : (('author', 'title', 'booktitle', 'publisher', 'date', ),
                      ('editor', 'volume', 'number', 'series', 'type',
                      'chapter', 'pages', 'address', 'edition',)),
    
    'InProceedings' : (('author', 'title', 'booktitle', 'date',),
                       ('editor', 'volume', 'number', 'series',
                       'pages', 'address', 'organization',
                       'publisher', 'note')),
    
    'Manual' : (('title',),
                ('author', 'organization', 'address', 'edition',
                 'date', 'note',)),
    
    'MastersThesis' : (('author', 'title', 'school', 'date',),
                       ('type', 'address', 'note',)),
    
    'Misc' : ((),
              ('author', 'title', 'howpublished', 'date', 'note',)),
    
    'PhdThesis' : (('author', 'title', 'school', 'date',),
                       ('type', 'address', 'note',)),
    
    'Proceedings' : (('title', 'date',),
                     ('editor', 'volume', 'number', 'series',
                     'address', 'publisher', 'note',
                      'organization',)),
    
    'TechReport' : (('author', 'title', 'institution', 'date',),
                    ('type', 'number', 'address', 'note',)),
    
    'Unpublished' : (('author', 'title', 'note',),
                     ('date',)),
    }

ent = {}
for e in entries.keys ():
    d = Types.EntryDescription (e)

    d.mandatory = \
        map (lambda x, desc=desc: desc [x], entries [e] [0])
    d.optional  = \
        map (lambda x, desc=desc: desc [x], entries [e] [1])

    ent [string.lower (e)] = d


Config.set ('base/fields', desc)
Config.set ('base/entries', ent)
Config.set ('base/defaulttype', ent ['article'])



