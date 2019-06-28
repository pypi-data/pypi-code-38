# -*- coding: utf-8 -*-

from dbmigrator import super_user


def up(cursor):
    with super_user() as cur:
        cur.execute("""\
-- Deprecated (3-Feb-2015) Use html_abstract(module_ident int)
--            This was deprecated to align the call params with
--            synonymous function cnxml_abstract, which requires
--            access to the module_ident to perform reference resolution.
CREATE OR REPLACE FUNCTION html_abstract(abstract text)
  RETURNS text
AS $$
  plpy.warning('This function is deprecated, please use html_abstract(<module_ident>')
  from cnxdb.triggers.transforms import transform_abstract_to_html
  html_abstract, warning_messages = transform_abstract_to_html(abstract, None, plpy)
  if warning_messages:
    plpy.warning(warning_messages)
  return html_abstract
$$ LANGUAGE plpythonu;

CREATE OR REPLACE FUNCTION html_abstract(module_ident int)
  RETURNS text
AS $$
  from cnxdb.triggers.transforms import transform_abstract_to_html
  plan = plpy.prepare("SELECT abstract FROM modules NATURAL JOIN abstracts WHERE module_ident = $1", ('integer',))
  abstract = plpy.execute(plan, (module_ident,))[0]['abstract']
  html_abstract, warning_messages = transform_abstract_to_html(abstract, module_ident, plpy)
  if warning_messages:
    plpy.warning(warning_messages)
  return html_abstract
$$ LANGUAGE plpythonu;

-- Deprecated (3-Feb-2015) Use html_content(module_ident int)
--            This was deprecated to align the call params with
--            synonymous function cnxml_content, which requires
--            access to the module_ident to perform reference resolution.
CREATE OR REPLACE FUNCTION html_content(cnxml text)
  RETURNS text
AS $$
  plpy.warning('This function is deprecated, please use html_content(<module_ident>')
  from cnxdb.triggers.transforms import transform_module_content
  html_content, warning_messages = transform_module_content(cnxml, 'cnxml2html', plpy)
  if warning_messages:
    plpy.warning(warning_messages)
  return html_content
$$ LANGUAGE plpythonu;

CREATE OR REPLACE FUNCTION html_content(module_ident int)
  RETURNS text
AS $$
  from cnxdb.triggers.transforms import transform_module_content
  plan = plpy.prepare("SELECT convert_from(file, 'utf-8') FROM module_files AS mf NATURAL JOIN files AS f WHERE module_ident = $1 AND (filename = 'index.cnxml' OR filename = 'index.html.cnxml')", ('integer',))
  cnxml = plpy.execute(plan, (module_ident,))[0]['convert_from']
  content, warning_messages = transform_module_content(cnxml, 'cnxml2html', plpy, module_ident)
  if warning_messages:
      plpy.warning(warning_messages)
  return content
$$ LANGUAGE plpythonu;


CREATE OR REPLACE FUNCTION cnxml_abstract(module_ident int)
  RETURNS text
AS $$
  from cnxdb.triggers.transforms import transform_abstract_to_cnxml
  plan = plpy.prepare("SELECT html FROM modules NATURAL JOIN abstracts WHERE module_ident = $1", ('integer',))
  abstract = plpy.execute(plan, (module_ident,))[0]['html']
  cnxml_abstract, warning_messages = transform_abstract_to_cnxml(abstract, module_ident, plpy)
  if warning_messages:
      plpy.warning(warning_messages)
  return cnxml_abstract
$$ LANGUAGE plpythonu;

CREATE OR REPLACE FUNCTION cnxml_content(module_ident int)
  RETURNS text
AS $$
  from cnxdb.triggers.transforms import transform_module_content
  plan = plpy.prepare("SELECT convert_from(file, 'utf-8') FROM module_files AS mf NATURAL JOIN files AS f WHERE module_ident = $1 AND filename = 'index.cnxml.html'", ('integer',))
  html = plpy.execute(plan, (module_ident,))[0]['convert_from']
  content, warning_messages = transform_module_content(html, 'html2cnxml', plpy, module_ident)
  if warning_messages:
      plpy.warning(warning_messages)
  return content
$$ LANGUAGE plpythonu;
""")


def down(cursor):
    with super_user() as cur:
        cur.execute("""\
-- Deprecated (3-Feb-2015) Use html_abstract(module_ident int)
--            This was deprecated to align the call params with
--            synonymous function cnxml_abstract, which requires
--            access to the module_ident to perform reference resolution.
CREATE OR REPLACE FUNCTION html_abstract(abstract text)
  RETURNS text
AS $$
  plpy.warning('This function is deprecated, please use html_abstract(<module_ident>')
  from cnxarchive.transforms import transform_abstract_to_html
  html_abstract, warning_messages = transform_abstract_to_html(abstract, None, plpy)
  if warning_messages:
    plpy.warning(warning_messages)
  return html_abstract
$$ LANGUAGE plpythonu;

CREATE OR REPLACE FUNCTION html_abstract(module_ident int)
  RETURNS text
AS $$
  from cnxarchive.transforms import transform_abstract_to_html
  plan = plpy.prepare("SELECT abstract FROM modules NATURAL JOIN abstracts WHERE module_ident = $1", ('integer',))
  abstract = plpy.execute(plan, (module_ident,))[0]['abstract']
  html_abstract, warning_messages = transform_abstract_to_html(abstract, module_ident, plpy)
  if warning_messages:
    plpy.warning(warning_messages)
  return html_abstract
$$ LANGUAGE plpythonu;

-- Deprecated (3-Feb-2015) Use html_content(module_ident int)
--            This was deprecated to align the call params with
--            synonymous function cnxml_content, which requires
--            access to the module_ident to perform reference resolution.
CREATE OR REPLACE FUNCTION html_content(cnxml text)
  RETURNS text
AS $$
  plpy.warning('This function is deprecated, please use html_content(<module_ident>')
  from cnxarchive.transforms import transform_module_content
  html_content, warning_messages = transform_module_content(cnxml, 'cnxml2html', plpy)
  if warning_messages:
    plpy.warning(warning_messages)
  return html_content
$$ LANGUAGE plpythonu;

CREATE OR REPLACE FUNCTION html_content(module_ident int)
  RETURNS text
AS $$
  from cnxarchive.transforms import transform_module_content
  plan = plpy.prepare("SELECT convert_from(file, 'utf-8') FROM module_files AS mf NATURAL JOIN files AS f WHERE module_ident = $1 AND (filename = 'index.cnxml' OR filename = 'index.html.cnxml')", ('integer',))
  cnxml = plpy.execute(plan, (module_ident,))[0]['convert_from']
  content, warning_messages = transform_module_content(cnxml, 'cnxml2html', plpy, module_ident)
  if warning_messages:
      plpy.warning(warning_messages)
  return content
$$ LANGUAGE plpythonu;


CREATE OR REPLACE FUNCTION cnxml_abstract(module_ident int)
  RETURNS text
AS $$
  from cnxarchive.transforms import transform_abstract_to_cnxml
  plan = plpy.prepare("SELECT html FROM modules NATURAL JOIN abstracts WHERE module_ident = $1", ('integer',))
  abstract = plpy.execute(plan, (module_ident,))[0]['html']
  cnxml_abstract, warning_messages = transform_abstract_to_cnxml(abstract, module_ident, plpy)
  if warning_messages:
      plpy.warning(warning_messages)
  return cnxml_abstract
$$ LANGUAGE plpythonu;

CREATE OR REPLACE FUNCTION cnxml_content(module_ident int)
  RETURNS text
AS $$
  from cnxarchive.transforms import transform_module_content
  plan = plpy.prepare("SELECT convert_from(file, 'utf-8') FROM module_files AS mf NATURAL JOIN files AS f WHERE module_ident = $1 AND filename = 'index.cnxml.html'", ('integer',))
  html = plpy.execute(plan, (module_ident,))[0]['convert_from']
  content, warning_messages = transform_module_content(html, 'html2cnxml', plpy, module_ident)
  if warning_messages:
      plpy.warning(warning_messages)
  return content
$$ LANGUAGE plpythonu;
""")
