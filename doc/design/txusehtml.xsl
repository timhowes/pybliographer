<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:output method="html"/>

  <xsl:template match="/">
    <xsl:variable name="ucn">
      <xsl:value-of select="usecase/@n"/>
    </xsl:variable>
    <html>
      <title>
        <xsl:text>Pybliographer Use Case (</xsl:text>
        <xsl:value-of select="substring($ucn,3,5)"/>
        <xsl:text>) </xsl:text>
        <xsl:value-of select="usecase/title"/>
      </title>

      
      <body bgcolor="#FFFFFF">
        <head><h1>
        <xsl:text>Pybliographer Use Case (</xsl:text>
        <xsl:value-of select="substring($ucn,3,5)"/>
        <xsl:text>) </xsl:text>
        <xsl:value-of select="usecase/title"/>
      </h1></head>
      <xsl:apply-templates/>
    </body>
  </html>
  </xsl:template>

  <xsl:template match="title"/>

  <xsl:template match="summary">
    <p><i><xsl:value-of select="."/></i></p>
  </xsl:template>


  <xsl:template match="precondition">
    <p><b>Precondition: </b>
    <xsl:value-of select="."/>
    </p>
  </xsl:template>


  <xsl:template match="postcondition">
    <p><b>Postcondition: </b>
    <xsl:value-of select="."/>
    </p>
  </xsl:template>


  <xsl:template match="context">
    <p><b>Context: </b>
    <xsl:value-of select="."/>
    </p>
  </xsl:template>

  <xsl:template match="error">
    <p><b>Error: </b>
    <xsl:value-of select="."/>
    </p>
  </xsl:template>

  <xsl:template match="note">
    <p><b>Note: </b>
    <xsl:value-of select="."/>
    </p>
  </xsl:template>




  <xsl:template match="related">
    <p><b>Related: </b>
    <xsl:value-of select="."/>
    </p>
  </xsl:template>

  <xsl:template match="actor">
    <p><b>Actor: </b>
    <xsl:value-of select="."/>
    </p>
  </xsl:template>

  <xsl:template match="sequence">
    <table width="100%" border="1" cellspacing="2" >
      <tr>
        <td bgcolor="#99CC99" colspan="2"><b>Sequence</b></td>
      </tr>
      <xsl:for-each select="item">
        <tr><td><xsl:value-of select="position()"/>
        <xsl:text>. </xsl:text>
        </td>
        <td><p><xsl:value-of select="."/></p></td>
        </tr>
      </xsl:for-each>
      
    </table>
  </xsl:template>



</xsl:stylesheet>
