import pygeoip
def coun(attackerip):
	ip_tocoun_db='GeoLiteCity.dat'
	gi = pygeoip.GeoIP(ip_tocoun_db) 
        # IP details are returend as a directory
	rec = gi.record_by_name(attackerip) 
	country = rec['country_name']
	country =str(country)
	return country 

