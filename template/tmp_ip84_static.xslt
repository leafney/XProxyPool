<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" >
<xsl:template match="/">
<proxyshow>
<xsl:apply-templates select="//*[@class='list']/tr[position()>=2 and count(./td[position()=1]/text())>0 and count(./td[position()=2]/text())>0 and count(./td[position()=3])>0 and count(./td[position()=4]/text())>0 and count(./td[position()=5]/text())>0]" mode="proxyshow"/>
</proxyshow>
</xsl:template>


<xsl:template match="//*[@class='list']/tr[position()>=2 and count(./td[position()=1]/text())>0 and count(./td[position()=2]/text())>0 and count(./td[position()=3])>0 and count(./td[position()=4]/text())>0 and count(./td[position()=5]/text())>0]" mode="proxyshow">
<item>
<xip>
<xsl:value-of select="td[position()=1]/text()"/>
</xip>
<xport>
<xsl:value-of select="td[position()=2]/text()"/>
</xport>
<xaddr>
<xsl:value-of select="td[position()=3]"/>
</xaddr>
<xlevel>
<xsl:value-of select="td[position()=4]/text()"/>
</xlevel>
<xprotocal>
<xsl:value-of select="td[position()=5]/text()"/>
</xprotocal>
</item>
</xsl:template>
</xsl:stylesheet>