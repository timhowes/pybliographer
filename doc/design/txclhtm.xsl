<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:output method="html" encoding="iso8859-1"/>
  <xsl:variable name="path" select="'/home/ptr/pamir/doc/design'" />

  <xsl:template match="/" mode="list">
    <html>
      <title>Pybliographer Classes</title>
      <body bgcolor="#FFFFFF">
        <head><h1>Pybliographer Classes</h1></head>

        <xsl:for-each select="listclasses/cl">
          <xsl:variable name="filename" >
            <xsl:value-of select="$path"/>
            <xsl:text>/data/cl_</xsl:text>
            <xsl:value-of select="./@file"/>
            <xsl:text>.xml</xsl:text>
          </xsl:variable>
          <xsl:apply-templates select="document($filename)/classinfo"
            mode="list" />
        </xsl:for-each>
      </body>
    </html>
  </xsl:template>


  <xsl:template match="/">
    <html>
      <head>
        <title>
          <xsl:text>Pybliographer Class </xsl:text>
          <xsl:value-of select="classinfo/title"/>
        </title>
      </head>
      <body bgcolor="#FFFFFF">
        <table width="100%">
          <tr>
            <td>
              <h1>
                <xsl:text>Class </xsl:text>
                <xsl:value-of select="classinfo/title"/>
              </h1>
            </td>
            <td><p><xsl:value-of select="classinfo/summary"/></p></td>
          </tr>
          
          <xsl:apply-templates>
          </xsl:apply-templates>
        </table>
      </body>
    </html>
  </xsl:template>



  <xsl:template match="classinfo" mode="list">
    <h2>      <xsl:value-of select="title"/>    </h2>
    <p>
      <xsl:value-of select="summary"/>
    </p>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="classinfo" mode="full">
    
    
  </xsl:template>


  <xsl:template match="title|summary"/>
    



</xsl:stylesheet>
