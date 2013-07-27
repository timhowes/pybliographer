# -*- coding: utf-8 -*-
# This file is part of pybliographer
# 
# Copyright (C) 1998-2004 Frederic GOBRY <gobry@pybliographer.org>
# Copyright (C) 2013 Germán Poo-Caamaño <gpoo@gnome.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2 
# of the License, or (at your option) any later version.
#   
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# 
# 

from gi.repository import Gtk

from Pyblio.GnomeUI import Utils

class MedlineUI (Utils.GladeWindow):

    gladeinfo = { 'name': 'medline',
                  'file': 'medline.ui',
                  'root': '_w_medline'
                  }

    def __init__(self, parent=None):
        Utils.GladeWindow.__init__(self, parent)

        # Fill in the combo boxes
        field_items = [ 'All Fields', 'Affiliation',
                        'Author Name', 'EC/RN Number',
                        'Entrez Date', 'Filter',
                        'Issue', 'Journal Name',
                        'Language', 'MeSH Date',
                        'MeSH Major Topic',
                        'MeSH Subheading', 'MeSH Terms',
                        'Pagination', 'Publication Date',
                        'Publication Type', 'Secondary Source ID',
                        'Substance Name', 'Text Word',
                        'Title', 'Title/Abstract',
                        'UID', 'Volume' ]
        for item in field_items:
            self._w_field.append_text(item)
        self._w_field.set_active(0)

        pub_type_items = [ 'Publication Types', 'Addresses',
                           'Bibliography', 'Biography',
                           'Classical Article', 'Clinical Conference',
                           'Clinical Trial', 'Clinical Trial, Phase I',
                           'Clinical Trial, Phase II', 'Clinical Trial, Phase III',
                           'Clinical Trial, Phase IV', 'Comment',
                           'Congresses', 'Consensus Development Conference',
                           'Consensus Development Conference, NIH',
                           'Controlled Clinical Trial',
                           'Corrected and Republished Article', 'Dictionary',
                           'Directory', 'Duplicate Publication',
                           'Editorial', 'Evaluation Studies',
                           'Festschrift', 'Government Publications',
                           'Guideline', 'Historical Article',
                           'Interview', 'Journal Article', 'Lectures',
                           'Legal Cases', 'Legislation', 'Letter',
                           'Meta-Analysis', 'Multicenter Study', 'News',
                           'Newspaper Article', 'Overall', 'Periodical Index',
                           'Practice Guideline', 'Published Erratum',
                           'Randomized Controlled Trial', 'Retraction of Publication',
                           'Retracted Publication', 'Review', 'Review, Academic',
                           'Review Literature', 'Review, Multicase',
                           'Review of Reported Cases', 'Review, Tutorial',
                           'Scientific Integrity Review', 'Technical Report',
                           'Twin Study', 'Validation Studies']
        for item in pub_type_items:
            self._w_pub_type.append_text(item)
        self._w_pub_type.set_active(0)


        language_items = [ 'Languages', 'English',
                           'French', 'German', 'Italian',
                           'Japanese', 'Russian', 'Spanish']
        for item in language_items:
            self._w_language.append_text(item)
        self._w_language.set_active(0)

        subset_items = [ 'Subsets', 'AIDS', 'AIDS/HIV journals',
                         'Bioethics', 'Bioethics journals',
                         'Biotechnology journals', 'Communication disorders journals',
                         'Complementary and Alternative Medicine',
                         'Consumer health journals', 'Core clinical journals',
                         'Dental journals', 'Health administration journals',
                         'Health tech assessment journals', 'History of Medicine',
                         'History of Medicine journals', 'In process',
                         'Index Medicus journals', 'MEDLINE', 'NASA journals',
                         'Nursing journals', 'PubMed Central', 'Reproduction journals',
                         'Space Life Sciences', 'Supplied by Publisher', 'Toxicology']
        for item in subset_items:
            self._w_subset.append_text(item)
        self._w_subset.set_active(0)

        age_items = [ 'Ages', 'All Infant: birth-23 month',
                      'All Child: 0-18 years', 'All Adult: 19+ years',
                      'Newborn: birth-1 month', 'Infant: 1-23 months',
                      'Preschool Child: 2-5 years', 'Child: 6-12 years',
                      'Adolescent: 13-18 years', 'Adult: 19-44 years',
                      'Middle Aged: 45-64 years', 'Aged: 65+ years',
                      '80 and over: 80+ years']
        for item in age_items:
            self._w_age.append_text(item)
        self._w_age.set_active(0)

        human_items = ['Human or Animal', 'Human', 'Animal']
        for item in human_items:
            self._w_human.append_text(item)
        self._w_human.set_active(0)

        gender_items = ['Gender', 'Female', 'Male']
        for item in gender_items:
            self._w_gender.append_text(item)
        self._w_gender.set_active(0)

        entrez_date_items = [ 'Entrez Date', '30 Days', '60 Days',
                              '90 Days', '180 Days', '1 Year', '2 Years',
                              '5 Years', '10 Years']
        for item in entrez_date_items:
            self._w_entrez_date.append_text(item)
        self._w_entrez_date.set_active(0)

        pub_date_items = ['Publication Date', 'Entrez Date']
        for item in pub_date_items:
            self._w_pub_date.append_text(item)
        self._w_pub_date.set_active(0)

        self._w_medline.show ()
        return

    
    def run (self):
        ret = self._w_medline.run ()

        if ret != Gtk.ResponseType.OK:
            self._w_medline.destroy ()
            return None

        data = (
            self._w_keyword.get_text(),
            self._w_max_results.get_value_as_int(),
            self._w_start_results.get_value_as_int(),
            self._w_field.get_active_text(),
            self._w_abstracts.get_active(),
            self._w_ahead.get_active(),
            self._w_pub_type.get_active_text(),
            self._w_language.get_active_text(),
            self._w_subset.get_active_text(),
            self._w_age.get_active_text(),
            self._w_human.get_active_text(),
            self._w_gender.get_active_text(),
            self._w_entrez_date.get_active_text(),
            self._w_pub_date.get_active_text(),
            self._w_from_date.get_text(),
            self._w_to_date.get_text()
            )
        
        self._w_medline.destroy ()

        return data
