<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" >
<xsl:template match="/">
<dailishow>
<xsl:apply-templates select="//*[@id='index_free_list']/table/tbody/tr[position()>=1 and count(./td[position()=1]/text())>0 and count(./td[position()=2]/text())>0 and count(./td[position()=3]/text())>0 and count(./td[position()=4]/text())>0 and count(./td[position()=6]/text())>0]" mode="dailishow"/>
</dailishow>
</xsl:template>


<xsl:template match="//*[@id='index_free_list']/table/tbody/tr[position()>=1 and count(./td[position()=1]/text())>0 and count(./td[position()=2]/text())>0 and count(./td[position()=3]/text())>0 and count(./td[position()=4]/text())>0 and count(./td[position()=6]/text())>0]" mode="dailishow">
<item>
<xip>
<xsl:value-of select="td[position()=1]/text()"/>
</xip>
<xport>
<xsl:value-of select="td[position()=2]/text()"/>
</xport>
<xlevel>
<xsl:value-of select="td[position()=3]/text()"/>
</xlevel>
<xprotocal>
<xsl:value-of select="td[position()=4]/text()"/>
</xprotocal>
<xaddr>
<xsl:value-of select="td[position()=6]/text()"/>
</xaddr>
</item>
</xsl:template>
</xsl:stylesheet>