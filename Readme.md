## Problem Statement

#### 1. Contact Data Scraping		

Scrape publicly available company data from their websites — focus only on what’s reliably accessible.		


| Field               | Status   | Notes                                           |
|---------------------|----------|-------------------------------------------------|
| Website URL         | Required | Use Google Search fallback if not provided  |
| General Contact Email | Required | Usually in “Contact Us” or page footer    |
| Phone Number        | Required | Found in footer or contact page             |
| Location / Address  | Required | Available on contact or “About” page        |
| Leadership Names    | Optional | Only if listed under “Team” or “Leadership” |

Output Required:
| Company | Website | Email | Phone | Location | Found Leadership Name(s) |
|---------|---------|-------|-------|----------|---------------------------|

---

#### 2. Technology Detection via Python		
		
For each company (list given), write a Python script to identify whether the website mentions:		
		
Cloud Technologies (e.g., AWS, Azure, GCP)		
MES Technologies (e.g., Siemens Opcenter, Rockwell FactoryTalk)		
PLM Technologies (e.g., Teamcenter, Windchill, ENOVIA)		

Output Required:

| Company   | Website                   | Cloud Tool Mentioned | Source URL                  | MES Tool Mentioned | Source URL                  | PLM Tool Mentioned | Source URL                  |
|-----------|---------------------------|-----------------------|-----------------------------|---------------------|-----------------------------|---------------------|-----------------------------|
| Company A | https://www.companya.com  | AWS                   | www.companya.com/tech       | Siemens Opcenter    | www.companya.com/tech       | -                   | www.companya.com/tech       |
| Company B | https://www.companyb.com  | GCP                   | www.companyb.com/products   | -                   | www.companyb.com/products   | Teamcenter          | www.companyb.com/products   |

---


### To use the Data Scraping Script for extracting details

---
Either use [Function7](function7.py) or [Function9](function9.py)

[error_correction.](error_correction.py)
Might not work well as some problems are occurring after
navigate_to_contact_page() - function

---

### Test on an unknown website, other than the 10 provided.
Script successfully fetched information from ifm's website, Including Contact number and Email Address, but got stuck collecting address details.
[Result](Test_Result.png)


---
### Run  below mentioned scripts for better results.
```bash
    function7.py
```

```bash
    function9.py
```

---
#### To convert an  Excel file to .csv, use this
```bash
    convert.py
```
---
