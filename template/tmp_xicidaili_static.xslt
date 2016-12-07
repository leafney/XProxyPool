<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" >
<xsl:template match="/">
<proxyshow>
<xsl:apply-templates select="//*[@id='ip_list']/tr[position()>=2 and count(./td[position()=2]/text())>0 and count(./td[position()=3]/text())>0 and count(./td[position()=4]/a/text())>0 and count(.//*[@class='country']/text())>0 and count(./td[position()=6]/text())>0]" mode="proxyshow"/>
</proxyshow>
</xsl:template>


<xsl:template match="//*[@id='ip_list']/tr[position()>=2 and count(./td[position()=2]/text())>0 and count(./td[position()=3]/text())>0 and count(./td[position()=4]/a/text())>0 and count(.//*[@class='country']/text())>0 and count(./td[position()=6]/text())>0]" mode="proxyshow">
<item>
<xip>
<xsl:value-of select="td[position()=2]/text()"/>
</xip>
<xport>
<xsl:value-of select="td[position()=3]/text()"/>
</xport>
<xaddr>
<xsl:value-of select="td[position()=4]/a/text()"/>
</xaddr>
<xlevel>
<xsl:value-of select="*//*[@class='country']/text()"/>
<xsl:value-of select="*[@class='country']/text()"/>
<xsl:if test="@class='country'">
<xsl:value-of select="text()"/>
</xsl:if>
</xlevel>
<xprotocal>
<xsl:value-of select="td[position()=6]/text()"/>
</xprotocal>
</item>
</xsl:template>
</xsl:stylesheet>