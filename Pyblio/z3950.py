#!/usr/bin/env python

# This file should be available from
# http://www.pobox.com/~asl2/software/PyZ39.50/
# and is licensed under the X Consortium license:
#          Copyright (c) 2001, Aaron S. Lav, asl2@pobox.com
#          All rights reserved.

#          Permission is hereby granted, free of charge, to any person obtaining a
#          copy of this software and associated documentation files (the
#          "Software"), to deal in the Software without restriction, including
#          without limitation the rights to use, copy, modify, merge, publish,
#          distribute, and/or sell copies of the Software, and to permit persons
#          to whom the Software is furnished to do so, provided that the above
#          copyright notice(s) and this permission notice appear in all copies of
#          the Software and that both the above copyright notice(s) and this
#          permission notice appear in supporting documentation.

#          THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#          OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#          MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
#          OF THIRD PARTY RIGHTS. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
#          HOLDERS INCLUDED IN THIS NOTICE BE LIABLE FOR ANY CLAIM, OR ANY SPECIAL
#          INDIRECT OR CONSEQUENTIAL DAMAGES, OR ANY DAMAGES WHATSOEVER RESULTING
#          FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
#          NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION
#          WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

#          Except as contained in this notice, the name of a copyright holder
#          shall not be used in advertising or otherwise to promote the sale, use
#          or other dealings in this Software without prior written authorization
#          of the copyright holder.


"""<p>PyZ39.50 currently is capable of sending and receiving v2 PDUs
Initialize, Search, Present, and Close.  There's a stab at abstracting
the protocol a bit in the Client and Server classes: they could use 
some work, especially in the areas of error handling and presenting a useful
API, but both interoperate with the <a href="http://www.indexdata.dk/yaz">
Yaz toolkit</a> and the client is capable of querying the Library of Congress.
More details will go in this docstring when you can actually use the code without
reading the source and being willing to put up with changing APIs.
<p>
Useful resources:
<ul>
<li><a href="http://lcweb.loc.gov/z3950/agency/">Library of Congress Z39.50 Maintenance Agency Page</a></li>
<li><a href="http://lcweb.loc.gov/z3950/agency/document.html">Official Specification</a></li>
<li><a href="http://www.loc.gov/z3950/agency/clarify/">Clarifications</a></li>
</ul>
"""
import asn1
import socket
import string
import re

vers = '0.6'
default_resultSetName = 'default'

DEFAULT_PORT = 210
DEFAULT_MAXR = 20   #default number of results returned, added by John Vu

Z3950_OID = [1,2,840,10003]
Z3950_ATTRS = Z3950_OID + [3]
Z3950_BIB_1 = Z3950_ATTRS + [1]
Z3950_USMARC = Z3950_OID + [5,10]
Z3950_SUTRS = Z3950_OID + [5, 101]
Z3950_VERS = 2 # This is a global switch: do we support V3 at all?  (The answer is no.)
# When we support V3, we also need per-connection state about whether v2 or v3 has been negotiated.

ProtocolVersion = asn1.TYPE (3, asn1.BITSTRING)
Options = asn1.TYPE (4, asn1.BITSTRING)
ReferenceId = asn1.TYPE (2, asn1.OCTSTRING)
if Z3950_VERS == 2:
    InternationalString = asn1.VisibleString
else:
    InternationalString = asn1.GeneralString # Except that we can negotiate restrictions at startup.

InfoCategory = asn1.SEQUENCE ([('categoryTypeId',1, asn1.OID, 1),
                               ('categoryValue', 2, asn1.INTEGER)])

OtherInfoInformation = asn1.CHOICE ([('characterInfo', 2, InternationalString),
                                     ('binaryInfo', 3, asn1.OCTSTRING),
                                     ('externallyDefinedInfo', 4, asn1.EXTERNAL),
                                     ('oid', 5, asn1.OID)])


OtherInfoElt = asn1.SEQUENCE ([('category', 1, InfoCategory),
                               ('information', None, OtherInfoInformation)])

OtherInformation = asn1.TYPE (201, asn1.SEQUENCE_OF (OtherInfoElt))


InitializeRequest = asn1.SEQUENCE([('referenceId', None, ReferenceId, 1),
                                    ('protocolVersion', None, ProtocolVersion),
                                    ('options', None, Options),
                                    ('preferredMessageSize', 5, asn1.INTEGER),
                                    ('exceptionalRecordSize', 6, asn1.INTEGER),
                                    ('idAuthentication', 7, asn1.ANY, 1),
                                    ('implementationId', 110, InternationalString, 1),
                                    ('implementationName', 111, InternationalString, 1),
                                    ('implementationVersion', 112, InternationalString, 1),
                                    ('userInformationField', 11, asn1.EXTERNAL, 1),
                                    ('otherInfo', None, OtherInformation, 1)])

InitializeResponse = asn1.SEQUENCE([('referenceId', None, ReferenceId, 1),
                                     ('protocolVersion', None, ProtocolVersion),
                                     ('options', None, Options),
                                     ('preferredMessageSize', 5, asn1.INTEGER),
                                     ('exceptionalRecordSize', 6, asn1.INTEGER),
                                     ('result', 12, asn1.BOOLEAN),
                                     ('implementationId', 110, InternationalString, 1),
                                     ('implementationName', 111, InternationalString, 1),
                                     ('implementationVersion', 112, InternationalString, 1),
                                     ('userInformationField', 11, asn1.EXTERNAL, 1),
                                     ('otherInfo', None, OtherInformation, 1)])


CloseReason = asn1.TYPE (211, asn1.INTEGER) # see std for enum'd vals

ResourceReportId = asn1.OID

StringOrNumeric = asn1.CHOICE ([('string', 1, InternationalString),
                                ('numeric', 2, asn1.INTEGER)])

Unit = asn1.SEQUENCE ([('unitSystem', 1, InternationalString,1),
                            ('unitType', 2, StringOrNumeric,1),
                            ('unit', 3, StringOrNumeric, 1),
                            ('scaleFactor', 4, asn1.INTEGER, 1)])

IntUnit = asn1.SEQUENCE ( [('value', 1, asn1.INTEGER),
                               ('unitUsed', 2, Unit)])

Estimate = asn1.SEQUENCE ([('type', 1, StringOrNumeric),
                                ('value', 2, IntUnit)])

ResourceReport = asn1.SEQUENCE ( [('estimates', 1, Estimate, 1),
                                      ('message', 2, InternationalString, 1)])

Close = asn1.SEQUENCE ([('referenceId', None, ReferenceId, 1),
                             ('closeReason', None, CloseReason),
                             ('diagnosticInformation', 3, InternationalString),
                             ('resourceReportFormat', 4, ResourceReportId, 1),
                             ('resourceReport', 5, ResourceReport, 1),
                             ('otherInfo', None, OtherInformation, 1)])
                              

DatabaseName = asn1.TYPE (105, InternationalString)
ElementSetName = asn1.TYPE (103, InternationalString)

dbspec = asn1.SEQUENCE ([('dbName', None, DatabaseName),
                         ('esn', None, ElementSetName)])

ElementSetNames = asn1.CHOICE ([('genericElementSetName', 0, InternationalString),
                                ('databaseSpecific', 1, asn1.SEQUENCE_OF (dbspec))])

PresentStatus = asn1.TYPE (27, asn1.INTEGER) # 0 success, partial-1 to partial-4, 5 failure
DefaultDiagFormat = asn1.SEQUENCE ([('diagnosticSetId', None, asn1.OID),
                                    ('condition', None, asn1.INTEGER),
                                    ('addinfo', None, asn1.CHOICE ([
    ('v2Addinfo', None, asn1.VisibleString),
    ('v3Addinfo', None, asn1.GeneralString)]))])

# DiagRec must be DefaultDiagFormat if v2 in effect
DiagRec = asn1.CHOICE ([('defaultFormat', None, DefaultDiagFormat),
                        ('externallyDefined', None, asn1.EXTERNAL)])

NamePlusRecord = asn1.SEQUENCE (
                                [('name', 0, DatabaseName, 1),
                                 ('record', asn1.EXPLICIT(1),
                                  asn1.CHOICE ([('retrievalRecord', asn1.EXPLICIT(1),
                                                 asn1.EXTERNAL),
                                                ('surrogateDiagnostic', asn1.EXPLICIT(2),
                                                 DiagRec)]))]) # and more for v3 l2 seg XXX



Records = asn1.CHOICE ([('responseRecords', 28, asn1.SEQUENCE_OF (NamePlusRecord)),
                        ('nonSurrogateDiagnostic', 130, DefaultDiagFormat),
                        ('multipleNonSurDiagnostics', 205, asn1.SEQUENCE_OF (DiagRec))])

AttributeSetId = asn1.OID

AttributeElement = asn1.SEQUENCE ([('attributeSet', 1, AttributeSetId, 1),
                                    ('attributeType', 120, asn1.INTEGER),
                                    ('attributeValueInteger', 121, asn1.INTEGER)]) # XXX v3 allows more complex

Term = asn1.TYPE (45, asn1.OCTSTRING) # XXX v3 allows more generality
                                        
AttributeList = asn1.TYPE (44, asn1.SEQUENCE_OF (AttributeElement))

apt = asn1.SEQUENCE ([('attributes', None, AttributeList),
                      ('term', None, Term)])
AttributesPlusTerm = asn1.TYPE (102, apt)

ResultSetId = asn1.TYPE (31, InternationalString)

resSetPlusAttr = asn1.SEQUENCE ([('resultSet', None, ResultSetId),
                                 ('attributes', None, AttributeList)])

ResultSetPlusAttributes = asn1.TYPE (214, resSetPlusAttr)

Operand = asn1.CHOICE ([('attrTerm', None, AttributesPlusTerm),
                        ('resultSet', None, ResultSetId),
                        ('resultAttr', None, ResultSetPlusAttributes)])
Operator = asn1.TYPE (asn1.EXPLICIT(46), asn1.CHOICE ([('and', 0, asn1.NULL),
                                        ('or', 1, asn1.NULL), 
                                        ('and-not', 2, asn1.NULL)])) # XXX v3 allows prox operator


RPNStructure = asn1.CHOICE ([('op', asn1.EXPLICIT(0), Operand),
                             ('rpnRpnOp', 1, asn1.SEQUENCE ([]))])

# set_arm is hack to allow recursive data structure.

rpnRpnOp = asn1.SEQUENCE ([('rpn1', None, RPNStructure),
                           ('rpn2', None, RPNStructure),
                           ('op', None, Operator)])

RPNStructure.set_arm (1, ('rpnRpnOp', 1, rpnRpnOp))

RPNQuery = asn1.SEQUENCE ([('attributeSet', None, AttributeSetId),
                                ('rpn', None, RPNStructure)])

Query = asn1.CHOICE ([('type-0', 0, asn1.ANY),
                      ('type-1', 1, RPNQuery),
                      ('type-2', 2, asn1.OCTSTRING),
                      ('type-100', 100, asn1.OCTSTRING),
                      ('type-101', 101, RPNQuery),
                      ('type-102', 102, asn1.OCTSTRING)])


SearchRequest = asn1.SEQUENCE ([('referenceId', None, ReferenceId, 1),
                                     ('smallSetUpperBound', 13, asn1.INTEGER),
                                     ('largeSetLowerBound', 14, asn1.INTEGER),
                                     ('mediumSetPresentNumber', 15, asn1.INTEGER),
                                     ('replaceIndicator', 16, asn1.BOOLEAN),
                                     ('resultSetName', 17, InternationalString),
                                     ('databaseNames', 18, asn1.SEQUENCE_OF (DatabaseName)),
                                     ('smallSetElementSetNames', 100, ElementSetNames, 1),
                                     ('mediumSetElementSetNames', 101, ElementSetNames, 1),
                                     ('preferredRecordSyntax', 104, asn1.OID, 1),
                                     ('query', asn1.EXPLICIT(21), Query),
                                     ('additionalSearchInfo', 203, OtherInformation, 1),
                                     ('otherInfo', None, OtherInformation, 1)])

SearchResponse = asn1.SEQUENCE ([('referenceId', None, ReferenceId, 1),
                                 ('resultCount', 23, asn1.INTEGER),
                                 ('numberOfRecordsReturned', 24, asn1.INTEGER),
                                 ('nextResultSetPosition', 25, asn1.INTEGER),
                                 ('searchStatus', 22, asn1.BOOLEAN),
                                 ('resultSetStatus', 26, asn1.INTEGER,1), # 1 subset, 2 interim, 3 none
                                 ('presentStatus', None, PresentStatus, 1),
                                 ('records', None, Records, 1),
                                 ('additionalSearchInfo', 203, OtherInformation, 1),
                                 ('otherInfo', None, OtherInformation, 1)])

Range = asn1.SEQUENCE ([('startingPosition', 1, asn1.INTEGER),
                         ('numberOfRecords', 2, asn1.INTEGER)])

PresentRequest = asn1.SEQUENCE ([('referenceId', None, ReferenceId, 1),
                                      ('resultSetId', None, ResultSetId),
                                      ('resultSetStartPoint', 30, asn1.INTEGER),
                                      ('numberOfRecordsRequested', 29, asn1.INTEGER),
                                      ('additionalRanges', 212, asn1.SEQUENCE_OF (Range), 1),
                                      ('recordComposition', 19, ElementSetNames,1), # XXX or CHOICE if v3
                                      ('preferredRecordSyntax', 104, asn1.OID, 1),
                                      ('maxSegmentCount', 204, asn1.INTEGER, 1),
                                      ('maxRecordSize', 206, asn1.INTEGER, 1),
                                      ('maxSegmentSize', 207, asn1.INTEGER, 1),
                                      ('otherInfo', None, OtherInformation, 1)])


PresentResponse = asn1.SEQUENCE ([('referenceId', None, ReferenceId,1),
                                       ('numberOfRecordsReturned', 24, asn1.INTEGER),
                                       ('nextResultSetPosition', 25, asn1.INTEGER),
                                       ('presentStatus', None, PresentStatus),
                                       ('records', None, Records, 1),
                                       ('otherInfo', None, OtherInformation, 1)])

PDU = asn1.CHOICE ([('initRequest', 20, InitializeRequest),
                    ('initResponse', 21, InitializeResponse),
                    ('searchRequest', 22, SearchRequest),
                    ('searchResponse', 23, SearchResponse),
                    ('presentRequest', 24, PresentRequest),
                    ('presentResponse', 25, PresentResponse),
                    ('close', 48, Close)])

# the following dictionaries were added by John Vu to clean up the MARC output somewhat
Status_Tag = {'a':'Increase in encoding level','c':'Corrected or revised','d':'Deleted','n':'New','p':'Increase in encoding level from prepublication'}

RecType_Tag = {'a':'Language material','c':'Notated music','d':'Manuscript notated music','e':'Cartographic material','f':'Manuscript cartographic material','g':'Projected medium','i':'Nonmusical sound recording','j':'Musical sound recording','k':'Two-dimensional nonprojectable graphic','m':'Computer file','o':'Kit','p':'Mixed material','r':'Three-dimensional artifact or naturally occurring object','t':'Manuscript language material'}

RecType_Tag_bibtex = {'a':'@BOOK','c':'@MISC','d':'@MISC','e':'@MISC','f':'@MISC','g':'@MISC','i':'@MISC','j':'@MISC','k':'@MISC','m':'@MISC','o':'@MISC','p':'@MISC','r':'@MISC','t':'@BOOK'}

BibLevel_Tag = {'a':'Monographic component part','b':'Serial component part','c':'Collection','d':'Subunit','i':'Integrating resource','m':'Monograph/item','s':'Serial'}

BibLevel_Tag_bibtex = {'a':'Monographic component part','b':'Serial component part','c':'Collection','d':'Subunit','i':'Integrating resource','m':'Monograph/item','s':'Serial'}

ControlType_Tag = {' ':'No specific type','#':'No specific type','a':'Archival'}

EncLevel_Tag = {' ':'Full level','1':'Full level, material not examined','2':'Less-than-full level, material not examined','3':'Abbreviated level','4':'Core level','5':'Partial (preliminary) level','7':'Minimal level','8':'Prepublication level','u':'Unknown','z':'Not applicable'}

CatalogForm_Tag = {' ':'Non-ISBD','#':'Non-ISBD','a':'AACR 2','i':'ISBD','u':'Unknown'}

LinkedRecRequire_Tag = {' ':'Related record not required','#':'Related record not required','r':'Related record required'}

MARC2bibtex_Tag = {'001': 'Control_Number', '003':'Control_Number_Identifier', '005': 'Date_and_Time_of_Latest_Transaction', '007':'Physical_Description_Fixed_Field_-_General_Information','008':'Fixed-Length_Data_Elements','010': 'LCCN','014': 'Link_to_Bibliographic_Record_for_Serial_or_Multipart_Item', '015':'National_bibliography_number','016': 'National_Bibliographic_Agency_Control_Number', '017':'Copyright_or_Legal_Deposit_Number',
            '020': 'ISBN','022':'International_Standard_Serial_Number', '028':'Publisher_Number','035': 'System_Control_Number','037':'Source_of_acquisition','040': 'Cataloging_Source','041':'Language_code','042': 'Authentication_Code','043': 'Geographic_Area_Code','045': 'Time_Period_of_Heading','047':'Form_of_Musical_Composition_Code',
            '050': 'Library_of_Congress_Call_Number','052': 'Geographic_Classification','053': 'LC_Classification_Number','055': 'National_Library_of_Canada_Call_Number','058': 'LC_Classification_Number_Assigned_in_Canada_[obsolete]_[CAN/MARC_only]','060': 'National_Library_of_Medicine_Call_Number','063': 'NLM_Classification_Number_Assigned_by_NLM_[obsolete]_[CAN/MARC_only]','066': 'Character_Sets_Present','068': 'NLM_Classification_Number_Assigned_in_Canada_[obsolete]_[CAN/MARC_only]','070': 'National_Agricultural_Library_Call_Number','072': 'Subject_Category_Code','073': 'Subdivision_Usage','080':'Universal_Decimal_Classification_Number','082': 'Dewey_Decimal_Call_Number','083': 'Dewey_Decimal_Classification_Number','086':'Government_Document_Call_Number','087': 'Government_Document_Classification_Number','088': 'Document_Shelving_Number_(CODOC)_[obsolete]_[CAN/MARC_only]','090':'Local_Call_Numbers','091':'Local_Call_Numbers','092':'Local_Call_Numbers','093':'Local_Call_Numbers','094':'Local_Call_Numbers','095':'Local_Call_Numbers','096':'Local_Call_Numbers','097':'Local_Call_Numbers','098':'Local_Call_Numbers','099':'Local_Call_Numbers',
            '100': 'AUTHOR','110': 'Heading_-_Corporate_Name','111': 'Heading_-_Meeting_Name','130': 'Heading_-_Uniform_Title','140': 'Uniform_Title_[obsolete]_[CAN/MARC_only]','143': 'Collective_Title_[obsolete]_[CAN/MARC_only]','150': 'Heading_-_Topical_Term','151': 'Heading_-_Geographic_Name','155': 'Heading_-_Genre/Form_Term','180': 'Heading_-_General_Subdivision','181': 'Heading_-_Geographic_Subdivision','182': 'Heading_-_Chronological_Subdivision','185': 'Heading_-_Form_Subdivision',
            '222':'Key_Title','240':'Uniform_Title','242':'Translation_of_Title_by_Cataloging_Agency','243':'Collective_Uniform_Title','245':'TITLE','246':'Varying_Forms_of_Title','247':'Former_Title_or_Title_Variations','250':'EDITION','254':'Musical_Presentation_Statement','257':'Country_of_producing_entity_for_archival_films','260':'Complex_See_Reference_-_Subject',
            '300':'Physical_Description','306':'Playing_Time','307':'Hours,_etc.','360': 'Complex_See_Also_Reference_-_Subject',
            '400': 'See_From_Tracing_-_Personal_Name','410': 'See_From_Tracing_-_Corporate_Name','411': 'See_From_Tracing_-_Meeting_Name','430': 'See_From_Tracing_-_Uniform_Title','440':'Series_Statement/Added_Entry_-_Title','450': 'See_From_Tracing_-_Topical_Term','451':'See_From_Tracing_-_Geographic_Name','455': 'See_From_Tracing_-_Genre/Form_Term','480': 'See_From_Tracing_-_General_Subdivision','481': 'See_From_Tracing_-_Geographic_Subdivision','482': 'See_From_Tracing_-_Chronological_Subdivision','485': 'See_From_Tracing_-_Form_Subdivision','490':'Series_Statement',
            '500': 'See_Also_From_Tracing_-_Personal_Name','504':'Bibliography_etc._note','505':'Formatted_contents_note','508':'Creation/Production_Credits_Note','510': 'Citations/References_Note','511': 'See_Also_From_Tracing_-_Meeting_Name','520':'Summary_etc._note','530': 'See_Also_From_Tracing_-_Uniform_Title','541':'Immediate_source_of_acquisition_note','550': 'See_Also_From_Tracing_-_Topical_Term','551': 'See_Also_From_Tracing_-_Geographic Name','555': 'See_Also_From_Tracing_-_Genre/Form Term','580': 'See_Also_From_Tracing_-_General_Subdivision','581': 'See_Also_From_Tracing_-_Geographic_Subdivision','582': 'See_Also_From_Tracing_-_Chronological_Subdivision','585': 'See_Also_From_Tracing_-_Form_Subdivision',
            '600':'Subject_added_entry-personal_name','640':'Series_Dates_of_Publication_and/or_Sequential_Designation','641': 'Series_Numbering_Peculiarities','642': 'Series_Numbering_Example','643': 'Series_Place_and_Publisher/Issuing_Body','644': 'Series_Analysis_Practice','645': 'Series_Tracing_Practice','646': 'Series_Classification_Practice','650':'Subject_Added_Entry_-_Topical_Term','655':'Index_term-genre/form','663': 'Complex_See_Also_Reference_-_Name','664': 'Complex_See_Reference_-_Name','665': 'History_Reference','666': 'General_Explanatory_Reference_-_Name','667': 'Nonpublic_General_Note','670': 'Source_Data_Found','671': 'Note_-_Work_Catalogued_(Names/Titles)_[obsolete]_[CAN/MARC_only]','675': 'Source_Data_Not_Found','676':'Note_-_Cataloging_Rules_(Names/Titles)_[obsolete]_[CAN/MARC only]','678': 'Biographical_or_Historical_Data','680': 'Public_General_Note','681': 'Subject_Example_Tracing_Note','682': 'Deleted_Heading_Information','685': 'Note_-_Source_Data_Found_(Subjects)_[obsolete]_[CAN/MARC_only]','686': 'Note_-_Source_Data_Not_Found_(Subjects)_[obsolete]_[CAN/MARC_only]','687': 'Note_-_Usage_(Subjects)_[obsolete]_[CAN/MARC_only]','688': 'Application_History_Note',
            '700': 'Established_Heading_Linking_Entry_-_Personal_Name','710': 'Established_Heading_Linking_Entry_-_Corporate_Name','711': 'Established_Heading_Linking_Entry_-_Meeting_Name','730': 'Established_Heading_Linking_Entry_-_Uniform_Title','740':'Added_Entry_-_Uncontrolled_Related/Analytical_Title','750': 'Established_Heading_Linking_Entry_-_Topical_Term','751': 'Established_Heading_Linking_Entry_-_Geographic_Name','755': 'Established_Heading_Linking_Entry_-_Genre/Form_Term','780':'Subdivision_Linking_Entry_-_General_Subdivision','781': 'Subdivision_Linking_Entry_-_Geographic_Subdivision','782': 'Subdivision_Linking_Entry_-_Chronological_Subdivision','785': 'Subdivision_Linking_Entry_-_Form_Subdivision','788': 'Complex_Linking_Entry_Data',
            '830':'Series_added_entry-uniform_title','852':'Location','856': 'Electronic_Location_and_Access','880': 'Alternate_Graphic_Representation',
            '900':'Local_data_element_A','901':'Local_data_element_B','903':'Local_data_element_C','904':'Local_data_element_D','905':'Local_data_element_E','906':'Local_data_element_F','907':'Local_data_element_G','908':'Put_command_parameter','920':'Collective_Biography','922':'Availability_of_service_copies','925':'Series_Statement_of_Reproduction','952':'Cluster_member','953':'Therapeutic_Classification','955':'Copy_-_level_information','985':'Local_Record_History','991':'Group'}

MARC_Tag = {'001': 'Control Number', '003':'Control Number Identifier', '005': 'Date and Time of Latest Transaction', '007':'Physical Description Fixed Field - General Information','008':'Fixed-Length Data Elements','010': 'Library of Congress Control Number','014': 'Link to Bibliographic Record for Serial or Multipart Item', '015':'National bibliography number','016': 'National Bibliographic Agency Control Number', '017':'Copyright or Legal Deposit Number',
            '020': 'International Standard Book Number','022':'International Standard Serial Number', '028':'Publisher Number','035': 'System Control Number','037':'Source of acquisition','040': 'Cataloging Source','041':'Language code','042': 'Authentication Code','043': 'Geographic Area Code','045': 'Time Period of Heading','047':'Form of Musical Composition Code',
            '050': 'Library of Congress Call Number','052': 'Geographic Classification','053': 'LC Classification Number','055': 'National Library of Canada Call Number','058': 'LC Classification Number Assigned in Canada [obsolete] [CAN/MARC only]','060': 'National Library of Medicine Call Number','063': 'NLM Classification Number Assigned by NLM [obsolete] [CAN/MARC only]','066': 'Character Sets Present','068': 'NLM Classification Number Assigned in Canada [obsolete] [CAN/MARC only]','070': 'National Agricultural Library Call Number','072': 'Subject Category Code','073': 'Subdivision Usage','080':'Universal Decimal Classification Number','082': 'Dewey Decimal Call Number','083': 'Dewey Decimal Classification Number','086':'Government Document Call Number','087': 'Government Document Classification Number','088': 'Document Shelving Number (CODOC) [obsolete] [CAN/MARC only]','090':'Local Call Numbers','091':'Local Call Numbers','092':'Local Call Numbers','093':'Local Call Numbers','094':'Local Call Numbers','095':'Local Call Numbers','096':'Local Call Numbers','097':'Local Call Numbers','098':'Local Call Numbers','099':'Local Call Numbers',
            '100': 'Heading - Personal Name','110': 'Heading - Corporate Name','111': 'Heading - Meeting Name','130': 'Heading - Uniform Title','140': 'Uniform Title [obsolete] [CAN/MARC only]','143': 'Collective Title [obsolete] [CAN/MARC only]','150': 'Heading - Topical Term','151': 'Heading - Geographic Name','155': 'Heading - Genre/Form Term','180': 'Heading - General Subdivision','181': 'Heading - Geographic Subdivision','182': 'Heading - Chronological Subdivision','185': 'Heading - Form Subdivision',
            '222':'Key Title','240':'Uniform Title','242':'Translation of Title by Cataloging Agency','243':'Collective Uniform Title','245':'Title Statement','246':'Varying Forms of Title','247':'Former Title or Title Variations','250':'Edition Statement','254':'Musical Presentation Statement','257':'Country of producing entity for archival films','260':'Complex See Reference - Subject',
            '300':'Physical Description','306':'Playing Time','307':'Hours, etc.','360': 'Complex See Also Reference - Subject',
            '400': 'See From Tracing - Personal Name','410': 'See From Tracing - Corporate Name','411': 'See From Tracing - Meeting Name','430': 'See From Tracing - Uniform Title','440':'Series Statement/Added Entry - Title','450': 'See From Tracing - Topical Term','451':'See From Tracing - Geographic Name','455': 'See From Tracing - Genre/Form Term','480': 'See From Tracing - General Subdivision','481': 'See From Tracing - Geographic Subdivision','482': 'See From Tracing - Chronological Subdivision','485': 'See From Tracing - Form Subdivision','490':'Series Statement',
            '500': 'See Also From Tracing - Personal Name','504':'Bibliography, etc. note','505':'Formatted contents note','508':'Creation/Production Credits Note','510': 'Citations/References Note','511': 'See Also From Tracing - Meeting Name','520':'Summary, etc. note','530': 'See Also From Tracing - Uniform Title','541':'Immediate source of acquisition note','550': 'See Also From Tracing - Topical Term','551': 'See Also From Tracing - Geographic Name','555': 'See Also From Tracing - Genre/Form Term','580': 'See Also From Tracing - General Subdivision','581': 'See Also From Tracing - Geographic Subdivision','582': 'See Also From Tracing - Chronological Subdivision','585': 'See Also From Tracing - Form Subdivision',
            '600':'Subject added entry-personal name','640':'Series Dates of Publication and/or Sequential Designation','641': 'Series Numbering Peculiarities','642': 'Series Numbering Example','643': 'Series Place and Publisher/Issuing Body','644': 'Series Analysis Practice','645': 'Series Tracing Practice','646': 'Series Classification Practice','650':'Subject Added Entry - Topical Term','655':'Index term-genre/form','663': 'Complex See Also Reference - Name','664': 'Complex See Reference - Name','665': 'History Reference','666': 'General Explanatory Reference - Name','667': 'Nonpublic General Note','670': 'Source Data Found','671': 'Note - Work Catalogued (Names/Titles) [obsolete] [CAN/MARC only]','675': 'Source Data Not Found','676':'Note - Cataloging Rules (Names/Titles) [obsolete] [CAN/MARC only]','678': 'Biographical or Historical Data','680': 'Public General Note','681': 'Subject Example Tracing Note','682': 'Deleted Heading Information','685': 'Note - Source Data Found (Subjects) [obsolete] [CAN/MARC only]','686': 'Note - Source Data Not Found (Subjects) [obsolete] [CAN/MARC only]','687': 'Note - Usage (Subjects) [obsolete] [CAN/MARC only]','688': 'Application History Note',
            '700': 'Established Heading Linking Entry - Personal Name','710': 'Established Heading Linking Entry - Corporate Name','711': 'Established Heading Linking Entry - Meeting Name','730': 'Established Heading Linking Entry - Uniform Title','740':'Added Entry - Uncontrolled Related/Analytical Title','750': 'Established Heading Linking Entry - Topical Term','751': 'Established Heading Linking Entry - Geographic Name','755': 'Established Heading Linking Entry - Genre/Form Term','780':'Subdivision Linking Entry - General Subdivision','781': 'Subdivision Linking Entry - Geographic Subdivision','782': 'Subdivision Linking Entry - Chronological Subdivision','785': 'Subdivision Linking Entry - Form Subdivision','788': 'Complex Linking Entry Data',
            '830':'Series added entry-uniform title','852':'Location','856': 'Electronic Location and Access','880': 'Alternate Graphic Representation',
            '900':'Local data element A','901':'Local data element B','903':'Local data element C','904':'Local data element D','905':'Local data element E','906':'Local data element F','907':'Local data element G','908':'Put command parameter','920':'Collective Biography','922':'Availability of service copies','925':'Series Statement of Reproduction','952':'Cluster member','953':'Therapeutic Classification','955':'Copy-level information','985':'Local Record History','991':'Group'}
# end of dictionaries added by John Vu


class Version (asn1.BitStringVal):
    def __init__ (self, usev3 = 1):
        v1 = 0
        v2 = 1
        v3 = 2
        asn1.BitStringVal.__init__ (self, v3)
        self.set_bits ((v1, v2))
        if usev3: self.set_bits ((v3,))
    def __repr__ (self):
        return "Version bits %d" % self.bits

class OptionsVal (asn1.BitStringVal):
    def __init__ (self):
        search = 0
        present = 1
        delSet = 2
        resourceReport = 3
        triggerResourceCtrl = 4
        resourceCtrl = 5
        accessCtrl = 6
        scan = 7
        sort = 8
        extendedServices = 10
        l1Seg = 11
        l2Seg = 12
        concurrentOperations = 13
        namedResultSets = 14
        asn1.BitStringVal.__init__ (self, namedResultSets)
        self.set_bits ((search, present)) # required support

def make_initreq ():
    InitReq = InitializeRequest ()
    InitReq.protocolVersion = Version (Z3950_VERS == 3)
    InitReq.options = OptionsVal ()
    # These msg sizes are pretty arbitrary -- we dynamically allocate no matter what
    InitReq.preferredMessageSize = 0x10000 
    InitReq.exceptionalRecordSize = 0x10000
    InitReq.implementationId = 'PyZ39.50 - contact asl2@pobox.com'  # haven't been assigned an official id #
    InitReq.implementationName = 'Test client'
    InitReq.implementationVersion = "%s (asn.1 %s)" % (vers, asn1.vers)
    return InitReq

def make_sreq (query, dbnames, rsn):
    sreq = SearchRequest ()
    sreq.smallSetUpperBound = 0
    sreq.largeSetLowerBound = 1
    sreq.mediumSetPresentNumber = 0
# as per http://lcweb.loc.gov/z3950/lcserver.html, Jun 07 2001, to work around Endeavor bugs in 1.13
    sreq.replaceIndicator = 1
    sreq.resultSetName = rsn
    sreq.databaseNames = dbnames
    sreq.query = ('type-1', query)
    return sreq


class parse_marc:
    def __init__ (self, s):
        self.marc = s
        print "Rec len", self.extract_int (0,4)
        print "Status:", self.marc[5]
        print "Type:", self.marc[6]
        print "Bibliographic level:", self.marc[7]
        print "Type of control:", self.marc[8]
        assert (self.marc[9] == ' ') # 'a' would be UCS/Unicode
        assert (self.marc[10] == '2' and self.marc[11] == '2')
        baseaddr = self.extract_int (12, 16)
        print "Encoding level:", self.marc[17]
        print "Descriptive cataloging form:", self.marc[18]
        print "Linked record requirement:", self.marc[19]
        assert (self.marc[20:22] == '45')
        pos = 24
        while pos < baseaddr:
            tag = self.marc[pos:pos+3]
            if tag [0] == '\035' or tag [0] == '\036':
                break
            fieldlen = self.extract_int (pos + 3, pos + 6)
            startpos = self.extract_int (pos + 7, pos + 11)
            pos = pos + 12
            line = self.marc[baseaddr + startpos:baseaddr + startpos + fieldlen]
            printline = string.replace (line, '\037', '$')
            # Warning: this replacement is for display purposes only!  '$' is perfectly
            # valid within a subfield!
            if printline == '':
                print "Empty tag", tag
                continue
            while printline[-1] == '\036' or printline [-1] == '\035':
                printline = printline [:-1]
            printline = string.replace (printline, '\035', '~')
            printline = string.replace (printline, '\036', '^')
            # print MARC_Tag[tag] + ':' + printline
            print tag, printline

    def extract_int (self, start, end):
        return string.atoi (self.marc[start:end+1])

class parse_marc2bibtex:  # added code by John Vu to parse MARC data for a single entry into bibtex, if possible
    def __init__ (self, s):
        self.marc = s

    def extract_rec (self):
        m = 0
        prevtag = ''
        uniformtitle = 0
        # print "Rec len", self.extract_int (0,4) # debugging; deprecated code
        # if Status_Tag.has_key(self.marc[5]): print "Status:", Status_Tag[self.marc[5]] #deprecated code, artifact from Aaron's original code
        if RecType_Tag.has_key(self.marc[6]): parsedresults = '\n' + RecType_Tag_bibtex[self.marc[6]] + '{\n'
        else: parsedresults = '\n@BOOK{,\n'
        # print "Bibliographic level:", BibLevel_Tag[self.marc[7]] #deprecated code, artifact from Aaron's original code
        # print "Type of control:", ControlType_Tag[self.marc[8]] #deprecated code, artifact from Aaron's original code
        assert (self.marc[9] == ' ') # 'a' would be UCS/Unicode
        assert (self.marc[10] == '2' and self.marc[11] == '2')
        baseaddr = self.extract_int (12, 16)
        # print "Encoding level:", EncLevel_Tag[self.marc[17]]  #deprecated code, artifact from Aaron's original code
        # print "Descriptive cataloging form:", CatalogForm_Tag[self.marc[18]]  #deprecated code, artifact from Aaron's original code
        # print "Linked record requirement:", LinkedRecRequire_Tag[self.marc[19]]  #deprecated code, artifact from Aaron's original code
        assert (self.marc[20:22] == '45')
        pos = 24
        while pos < baseaddr:
            tag = self.marc[pos:pos+3]
            if tag [0] == '\035' or tag [0] == '\036':
                break
            fieldlen = self.extract_int (pos + 3, pos + 6)
            startpos = self.extract_int (pos + 7, pos + 11)
            pos = pos + 12
            printline = self.marc[baseaddr + startpos:baseaddr + startpos + fieldlen]
            # I don't care about empty tags, nothing will be printed anyway
            while printline[-1] == '\036' or printline [-1] == '\035':
                printline = printline [:-1]
            printline = string.replace (printline, '\035', '~')
            printline = string.replace (printline, '\036', '^')
            printline = string.replace (printline, '\026', ' ') #some records have this character code which is CTRL-Z or EOF, and this causes pyblio to complain about an early EOF
            printline = string.strip (printline)
            if tag == '100': # author information
                subfields = re.split('\037', printline[1:]) # Subfields are separated by control key \037. Why split from printline[1:] and not printline[0:]? Because you'd get an empty subfield first and it'll spit out errors
                i = 0
                for subfield in subfields:
                    if subfield[0] == 'a':
                        subfield = string.strip (subfield)
                        parsedresults = parsedresults + '  AUTHOR = {' + subfield[1:] + '},\n'
                    elif subfield[0] == 'b':
                        subfield = string.strip (subfield)
                        parsedresults = parsedresults + '  AUTHOR_NUMERATION = {' + subfield[1:] + '},\n'
                    elif subfield[0] == 'c':
                        subfield = string.strip (subfield)
                        parsedresults = parsedresults + '  AUTHOR_TITLE' + `i` + ' = {' + subfield[1:] + '},\n'
                        i = i + 1
                    elif subfield[0] == 'd':
                        subfield = string.strip (subfield)
                        parsedresults = parsedresults + '  AUTHOR_DATE_OF_BIRTH/DEATH = {' + subfield[1:] + '},\n'
                    elif subfield[0] == 'q':
                        subfield = string.strip (subfield)
                        parsedresults = parsedresults + '  AUTHOR_FULL_NAME = {' + subfield[1:] + '},\n'
            elif tag == '240': # appears to be the title that is most widely used to designate the work
                subfields = re.split('\037', printline[1:])
                for subfield in subfields:
                    if subfield[0] == 'a':
                        subfield = string.replace (subfield, '/', '') #some titles have a weird frontslash at the end, this removes it
                        subfield = string.strip (subfield)
                        #subfield = string.capwords (subfield) #capitalizes the first letter of each word. I like to see my titles capitalized; however pyblio doesn't show the titles as such
                        parsedresults = parsedresults + '  TITLE = {' + subfield[1:] + '},\n'
                        uniformtitle = 1 #sometimes titles are at different places
                    elif subfield[0] == 'l':
                        subfield = string.strip (subfield)
                        parsedresults = parsedresults + '  LANGUAGE = {' + subfield[1:] + '},\n'
                    elif subfield[0] == 'f':
                        subfield = string.strip (subfield)
                        subfielddata = subfield[1:]
                        try:
                            while not subfield[-1].isdigit() and subfield[-1] <> ']' and subfield[-1] <> '?':
                                subfield = subfield[0:-1] #servers don't uniformly document years, I'm chopping away all that is not numbers at the end of the entry; secondly, sometimes there is no date which is designated as "[n.d.]"
                        except IndexError:
                            while subfielddata[0] == 'c': subfielddata = subfielddata[1:]
                            subfield = '[' + subfielddata + ']'
                        if subfield[0].isdigit() or subfield[0] == '[':
                            subfield = string.replace (subfield[0:], '[', '') # get rid of these ugly brackets
                            subfield = string.replace (subfield, ']', '')
                            parsedresults = parsedresults + '  YEAR = {' + subfield + '},\n'
                        elif subfield[1].isdigit() or subfield[1] == '[':
                            subfield = string.replace (subfield[1:], '[', '')
                            subfield = string.replace (subfield, ']', '')
                            parsedresults = parsedresults + '  YEAR = {' + subfield + '},\n'
                        elif subfield[2].isdigit() or subfield[2] == '[':
                            subfield = string.replace (subfield[2:], '[', '')
                            subfield = string.replace (subfield, ']', '')
                            parsedresults = parsedresults + '  YEAR = {' + subfield + '},\n'
            elif tag == '245': # title information
                subfields = re.split('\037', printline[1:])
                for subfield in subfields:
                    if subfield[0] == 'a':
                        subfield = string.strip (subfield)
                        fulltitle = subfield[1:]
                    elif subfield[0] == 'b':
                        subfield = string.strip (subfield)
                        fulltitle = fulltitle + subfield[1:]
                    elif subfield[0] == 'c':
                        subfield = string.replace(subfield, 'edited by', '')
                        subfield = string.replace(subfield, 'ed. by', '')
                        subfield = string.replace(subfield, 'Edited by', '')
                        subfield = string.replace(subfield, 'editors,', '')
                        subfield = string.replace(subfield, 'guest editors:', '')                        
                        subfield = string.replace(subfield, 'editor,', '')
                        subfield = string.replace(subfield, 'editor:', '')                        
                        subfield = string.replace(subfield, 'Editors:', '')
                        subfield = string.replace(subfield, '[]', '')                        
                        if subfield[1:2] == 'by':
                            subfield = subfield[0] + subfield[3:]
                        subfield = string.strip (subfield)
                        parsedresults = parsedresults + '  EDITOR = {' + subfield[1:] + '},\n'
                if uniformtitle: parsedresults = parsedresults + '  DESCRIPTION = {' + fulltitle + '},\n'
                else:
                    fulltitle = string.replace (fulltitle, '/', '')
                    fulltitle = string.strip (fulltitle)
                    #fulltitle = string.capwords (fulltitle) #capitalizes the first letter of each word. However pyblio doesn't show the titles as such
                    parsedresults = parsedresults + '  TITLE = {' + fulltitle + '},\n' # sometimes the title is split into two subfields, a title and then a subtitle, fulltitle is the join of the two
            elif tag == '260': # location, publisher, and year information
                subfields = re.split('\037', printline[1:])
                for subfield in subfields:
                    if subfield[0] == 'a':
                        subfield = string.replace (subfield, ':', '')
                        subfield = string.strip (subfield)
                        if subfield[-1] == ',' or subfield[-1] == '.': subfield = subfield[0:-1]
                        parsedresults = parsedresults + '  ADDRESS = {' + subfield[1:] + '},\n'
                    elif subfield[0] == 'b':
                        subfield = string.replace (subfield, ',', '')
                        subfield = string.strip (subfield)
                        parsedresults = parsedresults + '  PUBLISHER = {' + subfield[1:] + '},\n'
                    elif subfield[0] == 'c' and not uniformtitle:
                        subfield = string.strip (subfield)
                        subfielddata = subfield[1:]
                        try:
                            while not subfield[-1].isdigit() and subfield[-1] <> ']' and subfield[-1] <> '?':
                                subfield = subfield[0:-1] #servers don't uniformly document years, I'm chopping away all that is not numbers at the end of the entry; secondly, sometimes there is no date which is designated as "[n.d.]"
                        except IndexError:
                            while subfielddata[0] == 'c': subfielddata = subfielddata[1:]
                            subfield = '[' + subfielddata + ']'
                        if subfield[0].isdigit() or subfield[0] == '[':
                            subfield = string.replace (subfield[0:], '[', '') # get rid of these ugly brackets
                            subfield = string.replace (subfield, ']', '')
                            parsedresults = parsedresults + '  YEAR = {' + subfield + '},\n'
                        elif subfield[1].isdigit() or subfield[1] == '[':
                            subfield = string.replace (subfield[1:], '[', '')
                            subfield = string.replace (subfield, ']', '')
                            parsedresults = parsedresults + '  YEAR = {' + subfield + '},\n'
                        elif subfield[2].isdigit() or subfield[2] == '[':
                            subfield = string.replace (subfield[2:], '[', '')
                            subfield = string.replace (subfield, ']', '')
                            parsedresults = parsedresults + '  YEAR = {' + subfield + '},\n'
            elif tag == '300': # physical description
                subfields = re.split('\037', printline[1:])
                i = 0
                n = 0
                for subfield in subfields:
                    if subfield[0] == 'a': # number of pages
                        subfield = string.strip (subfield)
                        parsedresults = parsedresults + '  NUMBER_OF_PAGES' + `i` + ' = {' + subfield[1:] + '},\n'
                        i = i + 1
                    elif subfield[0] == 'b':
                        subfield = string.strip (subfield)
                        parsedresults = parsedresults + '  ILLUSTRATION = {' + subfield[1:] + '},\n'
                    elif subfield[0] == 'c':
                        subfield = string.strip (subfield)
                        parsedresults = parsedresults + '  DIMENSIONS' + `n` + ' = {' + subfield[1:] + '},\n'
                        n = n + 1
                    elif subfield[0] == 'e':
                        subfield = string.strip (subfield)
                        parsedresults = parsedresults + '  ACCOMPANYING_MATERIAL = {' + subfield[1:] + '},\n'
            elif tag == '856': #electronic location and access, nice for pyblio because of URL
                subfields = re.split('\037', printline[1:])
                for subfield in subfields:
                    if subfield[0] == 'u':
                        subfield = string.strip (subfield)
                        parsedresults = parsedresults + '  URL = {' + subfield[1:] + '},\n' 
            elif prevtag == tag and MARC2bibtex_Tag.has_key(tag): # bibtex doesn't like to have repeated fields. Some MARC fields can be repeated, this is a way to have repeating fields shown in bibtex
                subcounter = 0
                subfields = re.split('\037', printline[1:])
                for subfield in subfields:
                    subfield = string.strip (subfield)
                    if subfield <> '':
                        parsedresults = parsedresults + '  ' + MARC2bibtex_Tag[tag] + '-' + `m` + '.' + `subcounter` + ' = {' + subfield[1:] + '},\n'
                        subcounter = subcounter + 1
                m = m + 1
            elif MARC2bibtex_Tag.has_key(tag):
                m = 0
                subcounter = 0
                subfields = re.split('\037', printline[1:])
                for subfield in subfields:
                    subfield = string.strip (subfield)
                    if subfield <> '':
                        parsedresults = parsedresults + '  ' + MARC2bibtex_Tag[tag] + '-' + `m` + '.' + `subcounter` + ' = {' + subfield[1:] + '},\n'
                        subcounter = subcounter + 1
                m = m + 1
            prevtag = tag
        parsedresults = parsedresults + '}\n'
        return parsedresults

    def extract_int (self, start, end):
        return string.atoi (self.marc[start:end+1])

def disp_resp (resp): # this is Aaron Lav's original code
    (typ, recs) = resp.records
    if (typ <> 'responseRecords'):
        print "Bad records typ", typ
        print "records: ", recs
        return
    if len (recs) == 0:
        print "No records"
    for r in recs:
        (typ, data) = r.record
        if (typ <> 'retrievalRecord'):
            print "Bad typ", typ, "data", data
            continue
        oid = data.direct_reference
        dat = data.encoding
        if (oid <> asn1.OidVal (Z3950_USMARC)):
            print "Unknown OID", oid
            continue
        parse_marc (dat)
        print "\n"

def disp_rawresp (resp):  # This is code to show the query in raw MARC format, no parsing is done on the returned data; this is used for debugging purposes only
    (typ, recs) = resp.records
    if (typ <> 'responseRecords'):
        print "Bad records typ", typ
        print "records: ", recs
        return
    if len (recs) == 0:
        print "No records"
    for r in recs:
        (typ, data) = r.record
        if (typ <> 'retrievalRecord'):
            print "Bad typ", typ, "data", data
            continue
        oid = data.direct_reference
        dat = data.encoding
        print dat[1] #the data is in a tuple of 2 elements, the first is the OID type (dat[0]) and the second is the actual data, hence it's accessed here as "dat[1]"
        print "\n"

def disp_bibtex (resp): # This is added and modified code by John Vu attempting to parse the data from MARC to BibTeX format
    fullresults = ''
    try:
        (typ, recs) = resp.records
    except AttributeError:
        return fullresults  #if the search item is not found it'll spit an error saying: seq_class_24 instance has no attribute 'records'
    if (typ <> 'responseRecords'):
        return fullresults
    if len (recs) == 0:
        return fullresults
    else:
        for r in recs:
            (typ, data) = r.record
            if (typ <> 'retrievalRecord'):
                print "Bad typ", typ, "data", data #debugging
                continue
            oid = data.direct_reference
            dat = data.encoding
            if (oid <> asn1.OidVal (Z3950_USMARC)):
                print "Unknown OID", oid #debugging
                continue
            (marctyp, marcdat) = dat
            if marctyp <> 'octet-aligned':
                print "Weird record EXTERNAL MARC type", marctyp
            parsedentry = parse_marc2bibtex (marcdat)  # parses the query one entry at a time; perhaps here is where we can try to generate a key/identifier 
            fullresults = fullresults + parsedentry.extract_rec ()  # save each parsed entry in a full set to be returned after all entries are analyzed
    return fullresults

class Conn:
    rdsz = 65536
    def __init__ (self, sock = None):
        if sock == None:
            self.sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.ctx = asn1.Ctx (asn1.Ctx.dir_read)
        def readproc (s = self.sock, rdsz = self.rdsz):
            b = s.recv (rdsz)
            if len (b) == 0: # graceful close
                raise EOFError # hm.  is this the best way of handling this?
            return b
        self.ctx.set_data ("")
        self.ctx.set_readproc (readproc)
    def read_PDU (self):
        recv = PDU.decode (self.ctx)
        self.ctx.reset_read ()
        return recv
    
class Server (Conn):
    test = 0
    def __init__ (self, sock):
        Conn.__init__ (self, sock)
        self.expecting_init = 1
        self.done = 0
        self.result_sets = {}
        while not self.done:
            (typ, val) = self.read_PDU ()
            fn = self.fn_dict.get (typ, None)
            if fn == None:
                raise "Bad typ", typ  # should send close if OK, then close socket
            if typ <> 'initRequest' and self.expecting_init:
                raise "Init expected", typ
            fn (self, val)
    def send (self, val):
        b = asn1.encode (PDU, val)
        if self.test:
            print "Internal Testing" # a reminder not to leave this switched on by accident
            decoded = asn1.decode (PDU, b)
            assert (val== decoded)
        self.sock.send (b)

    def do_close (self, reason, info):
        close = Close ()
        close.closeReason = reason
        close.diagnosticInformation = info
        self.send (('close', close))

    def close (self, parm):
        print parm
        self.done = 1
        self.do_close (0, 'Normal close')
        
    def search_child (self, query):
        return range (10)
    def search (self, sreq):
        print "Search", sreq
        if sreq.replaceIndicator == 0 and self.result_sets.has_key (sreq.resultSetName):
            raise "replaceIndicator 0" # XXX spec says to reject politely
        # Should map search across sreq.databaseNames
        result = self.search_child (sreq.query)
        self.result_sets[sreq.resultSetName] = result
        sresp = SearchResponse ()
        sresp.resultCount = len (result)
        sresp.numberOfRecordsReturned = 0
        sresp.nextResultSetPosition = 0
        sresp.searchStatus = 1
        sresp.resultSetStatus = 0
        sresp.presentStatus = 0
        sresp.records = ('responseRecords', [])
        self.send (('searchResponse', sresp))
    def format_records (self, start, count, res_set, prefsyn):
        l = []
        sutrs = asn1.OidVal (Z3950_SUTRS)
        for i in range (start, start + count):
            elt = res_set[i]
            elt_external = asn1.EXTERNAL_STRUCT ()
            elt_external.direct_reference = sutrs
            # See Z39.50 clarification XXX - we really want GeneralString even when v2
            # is in force, although sending characters in the GeneralString but not
            # VisibleString repertoire might be bad.

            elt_external.encoding = asn1.encode (asn1.GeneralString,
                                                 'a silly placeholder %d' % elt).tostring ()
            n = NamePlusRecord ()
            n.name = 'foo'
            n.record = ('retrievalRecord', elt_external)
            l.append (n)
        return l
        
    def present (self, preq):
        print "Present", preq
        presp = PresentResponse ()
        res_set = self.result_sets [preq.resultSetId]
        presp.numberOfRecordsReturned = preq.numberOfRecordsRequested
        presp.nextResultSetPosition = preq.resultSetStartPoint + preq.numberOfRecordsRequested
        presp.presentStatus = 0
        presp.records = ('responseRecords',
                         self.format_records (preq.resultSetStartPoint, preq.numberOfRecordsRequested,
                                             res_set, preq.preferredRecordSyntax))
        print presp
        self.send (('presentResponse', presp))
        
    def init (self, ireq):
        print "Init", ireq
        ir = InitializeResponse () # Should negotiate
        ir.protocolVersion = Version (Z3950_VERS == 3)
        ir.options = OptionsVal ()
        ir.preferredMessageSize = 0x10000 
        ir.exceptionalRecordSize = 0x10000
        ir.implementationId = 'PyZ39.50 - contact asl2@pobox.com'
        # haven't been assigned an official id #
        ir.implementationName = 'Test server'
        ir.implementationVersion = "%s (asn.1 %s)" % (vers, asn1.pkg_version)
        ir.result = 1
        self.expecting_init = 0
        print ir
        self.send (('initResponse', ir))
    fn_dict = {'searchRequest': search,
               'presentRequest': present,
               'initRequest' : init,
               'close' : close}
        


def run_server ():
    listen = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    listen.setsockopt (socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen.bind ('', 9998)
    listen.listen (1)
    while 1:
        (sock,addr) = listen.accept ()
        print sock, addr
        try:
            serv = Server (sock)
        except:
            sock.close ()
            listen.close ()
            raise
        sock.close ()
        

class Client (Conn):
    test = 0
    def __init__ (self, addr, port = DEFAULT_PORT):
        Conn.__init__ (self)
        try:
            self.sock.connect ((addr, port))
        except socket.error, (errtype, errmessage):
            raise NameError, errmessage
        InitReq = make_initreq ()
        resp = self.transact (('initRequest', InitReq), 'initResponse')
        # required to support search and present, and that's all we asked for.
        self.search_results = {}
        self.max_to_request = 20   # change max number of returned results here accordingly
        self.default_recordSyntax = asn1.OidVal (Z3950_USMARC)
        # self.default_recordSyntax = asn1.OidVal (Z3950_SUTRS)  # uncomment this line if you want the data to be returned in SUTRS format
    def transact (self, to_send, expected):
        b = asn1.encode (PDU, to_send)
        if self.test:
            print "Internal Testing" # a reminder not to leave this switched on by accident
            decoded = asn1.decode (PDU, b)
            print decoded
            assert (to_send == decoded)
        self.sock.send (b)
        if expected == None:
            return
        (arm, val) = self.read_PDU ()
        if self.test:
            print "Internal Testing 2"
            b = asn1.encode (PDU, (arm, val))
            redecoded = asn1.decode (PDU, b)
            assert (redecoded == (arm, val))
        if arm == 'close':
            raise "Server closed connection reason %d diag info %s" % (val.closeReason,
                                                                       val.diagnosticInformation)
        elif arm == expected:
            return val
        else: raise "Unexpected response from server" + repr ((arm, val))
    def set_dbnames (self, dbnames):
        self.dbnames = dbnames
    def search (self, query, rsn = default_resultSetName):
        sreq = make_sreq (query, self.dbnames, rsn)
        recv = self.transact (('searchRequest', sreq), 'searchResponse')
        self.search_results [rsn] = recv
        assert (recv.numberOfRecordsReturned == 0) # we ask for no records in search,
        # see make_sreq for explanation
        return recv.searchStatus
    # If searchStatus is failure, check result-set-status - 
    # -subset - partial, valid results available
    # -interim - partial, not necessarily valid
    # -none - no result set
    # If searchStatus is success, check present-status:
    # - success - OK
    # - partial-1 - not all, access control
    # - partial-2 - not all, won't fit in msg size (but we currently don't ask for
    #               any records in search, shouldn't happen)
    # - partial-3 - not all, resource control (origin)
    # - partial-4 - not all, resource control (target)
    # - failure - no records, nonsurrogate diagnostic.

    def present (self, rsn= default_resultSetName, start = None, count = None, recsyn = None):
        sresp = self.search_results [rsn]
        if start == None:
            start = sresp.nextResultSetPosition
        if count == None:
            count = sresp.resultCount
            if self.max_to_request > 0:
                count = min (self.max_to_request, count)
        if recsyn == None:
            recsyn = self.default_recordSyntax
        preq = PresentRequest ()
        preq.resultSetId = rsn
        preq.resultSetStartPoint = start
        preq.numberOfRecordsRequested = count
        preq.preferredRecordSyntax = recsyn
        return self.transact (('presentRequest', preq), 'presentResponse')
