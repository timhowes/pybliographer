<?xml version="1.0"?>
<xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:output indent="yes" omit-xml-declaration="yes"/>

<xsl:template match="/">
 <xsl:apply-templates/>
</xsl:template>

<xsl:template match="module">
  <RefEntry>
    <RefNameDiv>
      <refname>Module <xsl:value-of select="@name"/></refname>
      <RefPurpose>
       Documentation for the module 
       <emphasis><xsl:value-of select="@name"/></emphasis>.
     </RefPurpose>
    </RefNameDiv>

    <refsynopsisdiv>
    <programlisting>
<xsl:for-each select="function">def <link><xsl:attribute name="linkend">
<xsl:value-of select="@id"/></xsl:attribute><xsl:value-of select="@name"/></link> (<xsl:for-each select="argument">
<xsl:value-of select="@name"/><xsl:if test="position()!=last()">, </xsl:if></xsl:for-each>):
</xsl:for-each><xsl:text>
</xsl:text><xsl:for-each select="variable"><xsl:text></xsl:text><xsl:value-of select="@name"/> = ...
</xsl:for-each>

<xsl:for-each select="class">
class <link><xsl:attribute name="linkend"><xsl:value-of select="@id"/></xsl:attribute>
<xsl:value-of select="@name"/></link>
<xsl:if test="count(parent)>0"> (<xsl:for-each select="parent">
<xsl:value-of select="@name"/><xsl:if test="position()!=last()">, </xsl:if></xsl:for-each>)</xsl:if>:

<xsl:for-each select="function">	def <link><xsl:attribute name="linkend">
<xsl:value-of select="@id"/></xsl:attribute><xsl:value-of select="@name"/></link> (<xsl:for-each select="argument">
<xsl:value-of select="@name"/><xsl:if test="position()!=last()">, </xsl:if></xsl:for-each>):
</xsl:for-each><xsl:text>
</xsl:text><xsl:for-each select="variable"><xsl:text>	</xsl:text><xsl:value-of select="@name"/> = ...
</xsl:for-each>
</xsl:for-each>
    </programlisting>
    </refsynopsisdiv>

    <refsect1><title>Module Description</title>
	<para><xsl:value-of select="documentation"/></para>
    </refsect1>

<xsl:for-each select="function">
    <refsect1><xsl:attribute name="id"><xsl:value-of select="@id"/></xsl:attribute>
      <title>Function <xsl:value-of select="@name"/></title>
      <para><xsl:value-of select="documentation"/></para>
    </refsect1>
</xsl:for-each>

<xsl:for-each select="class">
    <refsect1><xsl:attribute name="id"><xsl:value-of select="@id"/></xsl:attribute>
      <title>Class <xsl:value-of select="@name"/></title>
      <para><xsl:value-of select="documentation"/></para>

    <xsl:for-each select="function">
      <refsect2><xsl:attribute name="id"><xsl:value-of select="@id"/></xsl:attribute>
        <title><xsl:value-of select="@name"/> (<xsl:for-each select="argument">
<xsl:value-of select="@name"/><xsl:if test="position()!=last()">, </xsl:if>
</xsl:for-each>)</title>
      <para><xsl:value-of select="documentation"/></para>
      </refsect2>
    </xsl:for-each>
    </refsect1>
</xsl:for-each>
  </RefEntry>
</xsl:template>

<xsl:template match="argument">
<b><xsl:apply-templates/></b>
</xsl:template>

</xsl:transform>
