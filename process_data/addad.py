import tldextract

domain_tld = tldextract.extract('cdsfsdom.dadddddddd')
print domain_tld
print domain_tld.subdomain
print domain_tld.domain
print domain_tld.suffix