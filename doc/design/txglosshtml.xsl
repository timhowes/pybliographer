<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:output method="html" encoding="iso8859-1"/>
  <xsl:variable name="path" select="'/home/ptr/pamir/doc/design'" />
  <xsl:template match="/">
    <html>
      <title>Pybliographer Glossary</title>
      <body bgcolor="#FFFFFF">
        <head><h1>Pybliographer Glossary</h1></head>

        <xsl:for-each select="fullglossary/part">
          <xsl:variable name="filename" >
            <xsl:value-of select="$path"/>
            <xsl:text>/</xsl:text>
            <xsl:value-of select="./@n"/>
          </xsl:variable>
          <xsl:apply-templates select="document($filename)/glossary" />
        </xsl:for-each>
      </body>
    </html>
  </xsl:template>


  <xsl:template match="glossary">
    <h2><center><xsl:value-of select="@buchstabe"/></center></h2>
    <br/> 
    <xsl:apply-templates/>
  </xsl:template>

    

  <xsl:template match="GlossEntry">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="GlossEntry/GlossTerm">
    <h3><b><xsl:value-of select="."/>
    <xsl:if test="../Abbrev">
      <xsl:text> [</xsl:text>
      <xsl:value-of select="../Abbrev"/>
      <xsl:text>]</xsl:text>
    </xsl:if>
    <xsl:if test="../Acronym">
      <xsl:text> [</xsl:text>
      <xsl:value-of select="../Acronym"/>
      <xsl:text>]</xsl:text>
    </xsl:if>
  </b></h3>
  </xsl:template>

  <xsl:template match="Abbrev|Acronym">
    
  </xsl:template>
  <xsl:template match="GlossDef">
    <p><xsl:apply-templates/></p>
  </xsl:template>

  <xsl:template match="GlossSee">
    <i>see: </i><xsl:value-of select="."/>
  </xsl:template>

  <xsl:template match="GlossSeeAlso">
    <i>See also: </i><xsl:value-of select="."/>
  </xsl:template>

  <xsl:template match="GlossTerm">
    <i><xsl:value-of select="."/></i>
  </xsl:template>




</xsl:stylesheet>
