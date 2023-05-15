# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

#-------------------------------------------------------------
# Generic functions
#-------------------------------------------------------------

_translate_funcs = {}

def add_amount_to_text_function(lang, func):
    _translate_funcs[lang] = func
    
#TODO: we should use the country AND language (ex: septante VS soixante dix)
#TODO: we should use en by default, but the translation func is yet to be implemented
def amount_to_text(nbr, lang='fr', currency='euro'):
    """
    Converts an integer to its textual representation, using the language set in the context if any.
    Example:
        1654: mille six cent cinquante-quatre.
    """
#    if nbr > 1000000:
##TODO: use logger   
#        print "WARNING: number too large '%d', can't translate it!" % (nbr,)
#        return str(nbr)
    
    if not _translate_funcs.has_key(lang):
#TODO: use logger   
        print "WARNING: no translation function found for lang: '%s'" % (lang,)
#TODO: (default should be en) same as above
        lang = 'fr'
    return _translate_funcs[lang](abs(nbr), currency)

if __name__=='__main__':
    from sys import argv
    
    lang = 'nl'
    if len(argv) < 2:
        for i in range(1,200):
            print i, ">>", amount_to_text(i, lang)
        for i in range(200,999999,139):
            print i, ">>", amount_to_text(i, lang)
    else:
        print amount_to_text(int(argv[1]), lang)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

