from Pyblio import Config

Config.define ('base/fields', """ Existing fields.  It's a hash table,
               with the field name (lower case) as key, and a instance
               of Types.FieldDescription as value. """)

Config.define ('base/searched',
               """ fields that are searchable by default, and searched
               in a global search """)

Config.define ('base/entries', """ Existing entries.  It's a hash
               table, with the entry name (lower case) as key, and a
               instance of Types.EntryDescription as value. """)

Config.define ('base/defaulttype', """ Default type for a newly created entry """)

Config.define ('base/lyxpipe', """ Path to the LyX server """)
Config.set ('base/lyxpipe', '~/.lyx/lyxpipe')
