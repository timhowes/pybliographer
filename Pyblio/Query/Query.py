# This file is part of pybliographer
# 
# Copyright (C) 1998,1999,2000 Frederic GOBRY
# Email : gobry@idiap.ch
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
# $Id$

"""
Search a keyword in a medline database
or from a Z39.50 server

This code has been contributed by: John Vu <jvu001@umaryland.edu>
"""

# The time module is added for querying date ranges of publications
import urllib, sys, re, string, time
from Pyblio import z3950
from Pyblio import asn1

query_url = 'http://www.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
fetch_url = 'http://www.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'

def query_info (searchterm, field, displaynum, displaystart, edate):
    if edate != 'Entrez Date':
        params = urllib.urlencode ({
            'db': 'pubmed',
            'term' : searchterm,  # searchterm is user inputted text, modified by limits if applied
            'field' : field,
            'dopt' : 'd',
            'retmax' : displaynum,
            'retstart' : displaystart - 1, # minus 1 because the count starts at 0 and not at 1
            'reldate' : edate,  # two different search options given, depending on whether the user provides a relative entrez date
            'datetype' : 'edat',
            'usehistory' : 'n',
            'tool' : 'pybliographer',
            #'email' : 'johnvu@yahoo.com' # NCBI will email me about 
            })
    else:
        params = urllib.urlencode ({
            'db': 'pubmed',
            'term' : searchterm,  # searchterm is user inputted text, modified by limits
            'field' : field,
            'dopt' : 'd',
            'retmax' : displaynum,
            'retstart' : displaystart - 1,
            'usehistory' : 'n',
            'tool' : 'pybliographer',
            #'email' : 'johnvu@yahoo.com'
            })

    f = urllib.urlopen ("%s?%s" % (query_url, params))
    uids = []

    output = f.readlines ()
    for line in output:
        line = string.strip (line)
        if line[0:4] == '<Id>':
            line = string.replace (line,'<Id>','')
            line = string.replace (line,'</Id>','')
            uids.append (string.atoi(line))

    f.close ()
    return uids


def medline_query (keyword,maxcount,displaystart,field,abstract,epubahead,pubtype,language,subset,agerange,humananimal,gender,entrezdate,pubdate,fromdate,todate):
    # note all the parameters needed to perform the query
    # Search with field limits
    field_dict = {'All Fields': 'ALL','Affiliation': 'AFFL', 'Author Name': 'AUTH', 'EC/RN Number': 'ECNO', 'Entrez Date': 'EDAT', 'Filter': 'FLTR', 'Issue': 'ISS', 'Journal Name': 'JOUR', 'Language': 'LANG', 'MeSH Date': 'MHDA', 'MeSH Major Topic': 'MAJR', 'MeSH Subheading': 'SUBH', 'MeSH Terms': 'MESH', 'Pagination': 'PAGE', 'Publication Date':  'PDAT', 'Publication Type': 'PTYP', 'Secondary Source ID': 'SI', 'Substance Name': 'SUBS', 'Text Word': 'WORD', 'Title': 'TITL', 'Title/Abstract': 'TIAB', 'UID': 'UID', 'Volume': 'VOL'}
    publication_type = {'Addresses': ' AND addresses[pt]', 'Bibliography': ' AND bibliography[pt]', 'Biography': ' AND biography[pt]', 'Classical Article': ' AND classical article[pt]', 'Clinical Conference': ' AND clinical conference[pt]', 'Clinical Trial': ' AND clinical trial[pt]', 'Clinical Trial, Phase I': ' AND clinical trial, phase I[pt]', 'Clinical Trial, Phase II': ' AND clinical trial, phase II[pt]', 'Clinical Trial, Phase III': ' AND clinical trial, phase III[pt]', 'Clinical Trial, Phase IV': ' AND clinical trial, phase IV[pt]', 'Comment': ' AND comment[pt]', 'Congresses': ' AND congresses[pt]', 'Consensus Development Conference': ' AND consensus development conference[pt]', 'Consensus Development Conference, NIH': ' AND consensus development conference, NIH[pt]', 'Controlled Clinical Trial': ' AND controlled clinical trial[pt]', 'Corrected and Republished Article': ' AND corrected and republished article[pt]', 'Dictionary': ' AND dictionary[pt]', 'Directory': ' AND directory[pt]', 'Duplicate Publication': ' AND duplicate publication[pt]','Editorial': ' AND editorial[pt]','Evaluation Studies': ' AND evaluation studies[pt]','Festschrift': ' AND festschrift[pt]','Government Publications': ' AND government publications[pt]','Guideline': ' AND guideline[pt]','Historical Article': ' AND historical article[pt]','Interview': ' AND interview[pt]','Journal Article': ' AND journal article[pt]','Lectures': ' AND lectures[pt]','Legal Cases': ' AND legal cases[pt]','Legislation': ' AND legislation[pt]','Letter': ' AND letter[pt]','Meta-Analysis': ' AND meta-analysis[pt]','Multicenter Study': ' AND multicenter study[pt]','News': ' AND news[pt]','Newspaper Article': ' AND newspaper article[pt]','Overall': ' AND overall[pt]','Periodical Index': ' AND periodical index[pt]','Practice Guideline': ' AND practice guideline[pt','Published Erratum': ' AND published erratum[pt]','Randomized Controlled Trial': ' AND randomized controlled trial[pt]','Retraction of Publication': ' AND retraction of publication[pt]','Retracted Publication': ' AND retracted publication[pt]','Review': ' AND review[pt]','Review, Academic': ' AND review, academic[pt]','Review Literature': ' AND review, literature[pt]','Review, Multicase': ' AND review, multicase[pt]','Review of Reported Cases': ' AND review of reported cases[pt]','Review, Tutorial': ' AND review, tutorial[pt]','Scientific Integrity Review': ' AND scientific integrity review[pt]','Technical Report': ' AND technical report[pt]','Twin Study': ' AND twin study[pt]','Validation Studies': ' AND validation studies[pt]'}
    language_dict = {'English': ' AND english[la]', 'French': ' AND french[la]', 'German': ' AND german[la]', 'Italian': ' AND italian[la]', 'Japanese': ' AND japanese[la]', 'Russian': ' AND russian[la]', 'Spanish': ' AND spanish[la]'}
    subset_dict = {'AIDS':' AND aids[sb]', 'AIDS/HIV journals':' AND jsubsetx', 'Bioethics':' AND bioethics[ab]', 'Bioethics journals':' AND jsubsete', 'Biotechnology journals':' AND jsubsetb', 'Communication disorders journals':' AND jusbsetc', 'Complementary and Alternative Medicine':' AND cam[sb]', 'Consumer health journals':' AND jsubsetk', 'Core clinical journals':' AND jsubsetaim', 'Dental journals':' AND jsubsetd', 'Health administration journals':' AND jsubseth', 'Health tech assesment journals':' AND jsubsett', 'History of Medicine':' AND history[sb]', 'History of Medicine journals':' AND jsubsetq', 'In process':' AND in process[sb]', 'Index Medicus journals':' AND jsubsetim', 'MEDLINE':' AND medline[sb]', 'NASA journals':' AND jsubsets', 'Nursing journals':' AND jsubsetn', 'PubMed Central':' AND medline pmc[sb]', 'Reproduction journals':' AND jsubsetr', 'Space Life Sciences':' AND space[sb]', 'Supplied by Publisher':' AND publisher[sb]', 'Toxicology':' AND tox[sb]'}
    agerange_dict = {'All Infant: birth-23 month':' AND infant[mh]', 'All Child: 0-18 years':' AND child[mh]', 'All Adult: 19+ years':' AND adult[mh]', 'Newborn: birth-1 month':' AND infant, newborn[mh]', 'Infant: 1-23 months':' AND infant[mh]', 'Preschool Child: 2-5 years':' AND child, preschool[mh]', 'Child: 6-12 years':' AND child[mh]', 'Adolescent: 13-18 years':' AND adolescence[mh]', 'Adult: 19-44 years':' AND adult[mh]', 'Middle Aged: 45-64 years':' AND middle age[mh]', 'Aged: 65+ years':' AND aged[mh]', '80 and over: 80+ years':' AND aged, 80 and over[mh]'}
    entrezdate_dict = {'30 Days':'30', '60 Days':'60', '90 Days':'90', '180 Days':'180', '1 Year':'365', '2 Years':'730', '5 Years':'1825', '10 Years':'3650'}

    field = field_dict[field]
    
    # Below is added to keyword if user wants items with abstracts only
    if abstract: keyword = keyword + ' AND hasabstract'

    # Below is added to keyword if user wants items that are listed on pubmed ahead of print
    if epubahead: keyword = keyword + ' AND pubstatusaheadofprint'
    
    # Below are publication type limits to add to keyword
    if publication_type.has_key (pubtype):
        keyword = keyword + publication_type[pubtype]
    
    # Below are language limits to add to keyword if chosen

    if language_dict.has_key (language):
        keyword = keyword + language_dict[language]

    # Below are subset limits to add to keyword if chosen

    if subset_dict.has_key (subset):
        keyword = keyword + subset_dict[subset]

    # Age range will be added to keyword if desired

    if agerange_dict.has_key (agerange):
        keyword = keyword + agerange_dict[agerange]

    # Human or animal studies limit will be added to keyword if desired
    if humananimal == 'Human': keyword = keyword + ' AND human[mh]'
    elif humananimal == 'Animal': keyword = keyword + ' AND animal[mh]'

    # Studies done on either females or males will be a limit of keyword
    if gender == 'Female': keyword = keyword + ' AND female[mh]'
    elif gender == 'Male': keyword = keyword + ' AND male[mh]'
    
    # Past Entrez date range will be added to keyword; the number is the relative number of days prior to today
    if entrezdate_dict.has_key (entrezdate):
        entrezdate = entrezdate_dict[entrezdate]

    # if date limits are provided, then the following will be added to keyword
    # I will only allow this if the relative entrez date is not specified above, hence the elif command
    # This is where I used the time function, gmtime() to get the current global mean time
    elif fromdate != '':
        if todate == '':
            if pubdate == 'Publication Date': keyword = keyword + ' ' + fromdate + ':' + time.strftime('%Y/%m/%d', time.gmtime()) + '[dp]'
            elif pubdate == 'Entrez Date': keyword = keyword + ' ' + fromdate +':' + time.strftime('%Y/%m/%d',time.gmtime()) + '[edat]'
        else:
            if pubdate == 'Publication Date': keyword = keyword + ' ' + fromdate + ':' + todate + '[dp]'
            elif pubdate == 'Entrez Date': keyword = keyword + ' ' + fromdate + ':' + todate + '[edat]'

    # Below is the actual call to the URL (PubMed's cgi): first to gain the pubmed UIDs
    # and then to get the entries that is passed to pyblio to open
    uids = query_info (keyword, field, maxcount, displaystart, entrezdate) # get the pubmed UIDs and dump into uids variable
    
    uids = string.replace (str(uids),'[','') # I'm treating the uids list as one string. This will get rid of open bracket in string
    uids = string.replace (str(uids),']','') # get rid of close bracket in the string
    uids = string.replace (str(uids),' ','') # get rid of all the spaces in the string

    params = urllib.urlencode ({
        'db'     : 'pubmed',
        'report' : 'medline',
        'mode'   : 'text'
        })

    return "%s?%s&id=%s" % (fetch_url, params, str(uids))

def z3950_query (server,port,database,displaystart,maxresults,term1,term1attribute,term2,term2attribute,operator):
    attValueDict = {'All Fields':1035, 'Any Fields':1035, 'Author':1003, 'Personal Author (Last, First)':1, 'Personal Name':1, 'Corporate Name':2, 'Conference Name':3, 'Title (Phrase)':5, 'Title (Word)':4, 'Uniform Title':6, 'Keywords':21, 'Subject':21, 'Subject (Authorized)':27, 'Year':30, 'Date of Publication':31, 'Key Title (serials)':33, 'ISBN':7, 'ISSN':8, 'LCCN':9, 'LC Call Number':16, 'Subject (Personal Name)':1009, 'Publisher\'s Number':51, 'Geographic Name':58, 'Note':63, 'Electronic access':1032} #dictionary for attributeValueInteger that targets search query to category
    bib1 = asn1.OidVal (z3950.Z3950_BIB_1)
    try: 
        cli = z3950.Client (server, port)
        cli.set_dbnames ([database])
    except (EOFError, NameError):
        raise NameError, 'Can\'t connect to server'
    rpnq = z3950.RPNQuery (attributeSet = bib1)
    aelt1 = z3950.AttributeElement (attributeType = 1, attributeValueInteger = attValueDict[term1attribute])
    apt1 = z3950.apt ()
    apt1.attributes = [aelt1]
    apt1.term = term1
    term2 = string.strip (term2)
    if term2 <> '':
        aelt2 = z3950.AttributeElement (attributeType = 1, attributeValueInteger = attValueDict[term2attribute])
        apt2 = z3950.apt ()
        apt2.attributes = [aelt2]
        apt2.term = term2
        rpnq = z3950.RPNQuery (attributeSet = bib1)
        rpnRpnOp = z3950.rpnRpnOp ()
        rpnRpnOp.rpn1 = ('op', ('attrTerm', apt1))
        rpnRpnOp.rpn2 = ('op', ('attrTerm', apt2))
        rpnRpnOp.op = (operator, None)
        rpnq.rpn = ('rpnRpnOp', rpnRpnOp)
    else:
        rpnq = z3950.RPNQuery (attributeSet = bib1)
        rpnq.rpn = None
        rpnq.rpn = ('op', ('attrTerm', apt1))
    if cli.search (rpnq):
        bibtexresults = z3950.disp_bibtex (cli.present (start = displaystart, count = maxresults))
        return bibtexresults
    else:
        print "Not found"

def spires_query (server,author,title,c,reportnum,affiliation,cn,k,cc,eprint,eprint_num,topcit,url,j,ps,date,year,format,sequence):
    server_dict = {'UK':'http://www-spires.dur.ac.uk/spires/find/hep/www','USA':'http://www.slac.stanford.edu/spires/find/hep/www','Japan':'http://www.yukawa.kyoto-u.ac.jp/spires/find/hep/www','Russia':'http://usparc.ihep.su/spires/find/hep/www','Germany':'http://www-library.desy.de/spires/find/hep/www'}
    journal_dict = {'Any Journal':'','ACTA PHYS. AUSTR.':'APASA','ACTA PHYS. POLON.':'APPOA','ANN. POINCARE':'AHPAA','ANN. PHYS. (N.Y.)':'APNYA','ASTROPHYS. J.':'ASJOA','CAN. J. PHYS.':'CJPHA','CLASS. QUANT. GRAV.':'CQGRD','COMM. NUCL. PART. PHYS.':'CNPPA','COMMUN. MATH. PHYS.':'CMPHA','COMMUN. THEOR. PHYS.':'CTPMD','COMPUT. PHYS. COMMUN.':'CPHCB','CZECH. J. PHYS.':'CZYPA','EUROPHYS. LETT.':'EULEE','EUR. PHYS. J.':'EPHJA','FIZ. ELEM. CHAST. AT. YADRA':'FECAA','FIZIKA':'FZKAA','FORTSCHR. PHYS.':'FPYKA','FOUND. PHYS.':'FNDPA','GEN. REL. GRAV.':'GRGVA','HADRONIC J.':'HADJM','HELV. PHYS. ACTA':'HPACA','HIGH ENERGY PHYS. NUCL. PHYS.':'KNWLD','IEEE TRANS. MAGNETICS':'IEMGA','IEEE TRANS. NUCL. SCI.':'IETNA','INSTRUM. EXP. TECH.':'INETA','INT. J. MOD. PHYS.':'IMPAE','INT. J. THEOR. PHYS.':'IJTPB','JHEP':'JHEPA','J. MATH. PHYS.':'JMAPA','J. PHYS. - A -':'JPAGB','J. PHYS. - G -':'JPHGB','J. PHYS. SOC. JAP.':'JUPSA','JETP LETT.':'JTPLA','LETT. MATH. PHYS.':'LMPHD','LETT. NUOVO CIM.':'NCLTA','MOD. PHYS. LETT.':'MPLAE','New J. Phys.':'NJP','NUCL. INSTRUM. METH.':'NUIMA','NUCL. PHYS.':'NUPHA','NUOVO CIM.':'NUCIA','PART. ACCEL.':'PLACB','PHYS. ATOM. NUCL.':'PANUE','PHYS. LETT.':'PHLTA','PHYS. REPT.':'PRPLC','PHYS. REV.':'PHRVA','PHYS. REV. LETT.':'PRLTA','PHYS. SCRIPTA':'PHSTB','PHYSICA':'PHYSA','PISMA ZH. EKSP. TEOR. FIZ.':'ZFPRA','PRAMANA':'PRAMC','PROG. PART. NUCL. PHYS.':'PPNPD','PROG. THEOR. PHYS.':'PTPKA','REPT. MATH. PHYS.':'RMHPB','REPT. PROG. PHYS.':'RPPHA','REV. MOD. PHYS.':'RMPHA','REV. SCI. INSTRUM.':'RSINA','RIV. NUOVO CIM.':'RNCIB','RUSS. PHYS. J. (SOV. PHYS. J.)':'SOPJA','SOV. J. NUCL. PHYS.':'SJNCA','SOV. PHYS. JETP':'SPHJA','TEOR. MAT. FIZ.':'TMFZA','THEOR. MATH. PHYS.':'TMPHA','YAD. FIZ.':'YAFIA','Z. PHYS.':'ZEPYA','ZH. EKSP. TEOR. FIZ.':'ZETFA'}
    seq_sort_dict = {'No Sort':'','Note: Sorting can be slow':'','Date Order - Descending':'ds(d)','Date Order - Ascending':'ds(a)','1st Author':'AU','Title':'T','1st Author, Title':'AU,T'}
    date_dict = {'Select':'','During':'IN','Before':'BEFORE','After':'AFTER'}

    if eprint == 'Any Type': eprint = ''
    if topcit == 'Don\'t care': topcit = ''
    if url == 'Yes':
        rpp = 'pdg-rpp'
    else:
        rpp = ''
    if ps == 'Don\'t care': ps = ''
    if year == 'Any Year': year = ''
    if date == 'Select':
        date =  date_dict[date]
    else:
        date =  date_dict[date] + '&*=' + year

    params = urllib.urlencode ({
        'AUTHOR' : author,
        'TITLE' : title,
        'C' : c,
        'REPORT-NUM' : reportnum,
        'AFFILIATION' : affiliation,
        'cn' : cn,
        'k' : k,
        'cc' : cc,
        'eprint' : '+'+eprint,
        'eprint' : eprint_num,
        'topcit' : topcit,
        'url' : rpp,
        'j' : journal_dict[j],
        'ps' : ps,
        'FORMAT' : format,
        'SEQUENCE' : seq_sort_dict[sequence]
        })

    return "%s?%s&date=%s" % (server_dict[server], params, date)
