<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:output method="html"/>

  <xsl:template match="/">
    <html>
      <title>
        List of Pybliographer Use Cases
      </title>

      
      <body bgcolor="#FFFFFF">
        <head><h1>Pybliographer Use Cases</h1></head>
        <xsl:apply-templates/>
      </body>
    </html>
  </xsl:template>


  <xsl:template match="uc">
    <xsl:variable name="n" select="@filename"/>
    <xsl:variable name="filename">
      <xsl:text>/home/ptr/pamir/doc/design/data/uc</xsl:text>
      <xsl:value-of select="$n"/>
      <xsl:text>.xml</xsl:text>
    </xsl:variable>

    <h2>
      <xsl:value-of select="$n"/>      <xsl:text> - </xsl:text>
      <!-- xsl:value-of select="$filename"/ -->
      <xsl:value-of select="document($filename)/usecase/title"/>
    </h2>

    <p><xsl:value-of select="document($filename)/usecase/summary"/></p>

    <xsl:apply-templates/>

    <hr />
  </xsl:template>


  <xsl:template match="precondition">
    <p><b>Precondition: </b>
    <xsl:value-of select="."/>
  </p>
  </xsl:template>
</xsl:stylesheet>
