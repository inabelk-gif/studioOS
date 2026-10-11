"""Watch-list of Jerusalem companies (from Компании_по_районам_v4.xlsx).

Each company has:
- `aliases`: names (English/Hebrew) used to recognise the company on job
  boards (LinkedIn, AllJobs, Drushim, JobMaster). Matched as whole words
  against the vacancy's company name.
- `watch` (optional): how to check the company's own careers site daily:
    ("lever", "<company>")                     — Lever EU postings API
    ("greenhouse", "<board>")                  — Greenhouse board API
    ("workday", "<host>", "<tenant>", "<site>") — Workday jobs API
    ("bamboohr", "<company>")                  — BambooHR careers list
    ("sitemap", "<sitemap url>", "<path>")     — job pages listed in the
                                                 site's sitemap.xml under
                                                 <path>; title from the URL
    ("page", "<url>")                          — plain careers page; any
                                                 line that looks like a
                                                 design job title is reported
Companies without `watch` are only recognised on the job boards.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class Company:
    name: str
    aliases: List[str] = field(default_factory=list)
    watch: Optional[Tuple[str, ...]] = None


WATCHED_COMPANIES: List[Company] = [
    # Har Hotzvim
    Company("Medtronic", ["Medtronic", "Covidien", "Oridion", "מדטרוניק"],
            ("workday", "medtronic.wd1.myworkdayjobs.com", "medtronic", "MedtronicCareers")),
    Company("משטרת ישראל", ["משטרת ישראל", "Israel Police"]),
    Company("Teva", ["Teva", "טבע"]),
    Company("Mobileye", ["Mobileye", "מובילאיי"],
            ("lever", "mobileye")),
    Company("Cisco", ["Cisco", "סיסקו"],
            ("workday", "cisco.wd5.myworkdayjobs.com", "cisco", "Cisco_Careers")),
    Company("RAD", ["RAD", "RAD Data Communications", "רד תקשורת"],
            ("page", "https://www.rad.com/career/")),
    Company("Radware", ["Radware", "רדוור"]),
    Company("MalamTeam", ["MalamTeam", "Malam Team", "מלם תים", "מלם-תים"]),
    Company("Abra", ["Abra", "אברה"],
            ("page", "https://www.abra-it.com/career/")),
    Company("Ophir / MKS", ["Ophir", "MKS Instruments", "אופיר"]),
    Company("Ericom / Cradlepoint", ["Ericom", "Cradlepoint", "אריקום"]),
    Company("AppLogic Networks (Sandvine)", ["AppLogic Networks", "Sandvine"],
            ("page", "https://www.applogicnetworks.com/company/careers")),
    Company("Umoove", ["Umoove"]),
    # Talpiot
    Company("200Apps", ["200Apps", "200 Apps"],
            ("page", "https://www.200apps.com/career")),
    Company("FatFish", ["FatFish", "Fat Fish", "פאטפיש"],
            ("page", "https://www.fatfish.co.il/join-us")),
    Company("Nevelis", ["Nevelis", "נבליס"]),  # site moved to nevelis.com
    Company("ewave (Softwatch)", ["Softwatch", "ewave", "איוויב"]),
    Company("Matrix", ["Matrix", "מטריקס"],
            ("page", "https://www.matrix.co.il/jobs/")),
    Company("Dexel Print", ["Dexel", "דקסל"]),
    Company("Grafoprint", ["Grafoprint", "גרפופרינט"]),
    # Givat Shaul
    Company("Hometalk / Vernet", ["Hometalk", "Vernet", "Networx"]),
    Company("Koren Publishers", ["Koren", "Maggid", "קורן"]),
    Company("Teldan", ["Teldan", "טלדן"]),
    # Givat Ram
    # The Greenhouse board is empty; open jobs are listed as /career/...
    # pages in the main site's sitemap.
    Company("Lightricks", ["Lightricks", "לייטריקס"],
            ("sitemap", "https://www.lightricks.com/sitemap.xml", "/career/")),
    Company("Yissum", ["Yissum", "יישום"]),
    Company("Alpha Omega", ["Alpha Omega", "אלפא אומגה"],
            ("page", "https://www.alphaomega-eng.com/Careers")),
    Company("Compumat", ["Compumat", "קומפומט"]),
    Company("Ajinomatrix", ["Ajinomatrix"]),
    # City centre, academia, government
    Company("מערך הסייבר הלאומי", ["מערך הסייבר", "National Cyber Directorate"]),
    Company("LeverageIT (illuminea)", ["illuminea", "LeverageIT", "Leverage IT"],
            ("page", "https://leverage.it/careers/")),
    Company("Bagel Studio", ["Bagel Studio", "בייגל סטודיו"]),  # bagelstudio.co.il
    Company("Beyond Designs", ["Beyondesigns", "Beyond Designs"]),  # beyondesigns.net
    Company("Atreo", ["Atreo"]),
    Company("Goldfish Marketing", ["Goldfish Marketing"]),  # goldfishmarketing.co.il
    Company("Dofinity", ["Dofinity", "דופיניטי"]),
    Company("Quickode", ["Quickode"]),
    Company("האוניברסיטה העברית", ["האוניברסיטה העברית", "Hebrew University", "HUJI"]),
    Company("בצלאל", ["בצלאל", "Bezalel"],
            ("page", "https://www.bezalel.ac.il/about/suppliers-tenders")),
    Company("מוזיאון ישראל", ["מוזיאון ישראל", "Israel Museum"]),
    # Suburbs
    Company("Say", ["Say Brand", "Say Studio"]),  # saybrand.co.il, Ein Karem
    Company("Y-Tech", ["Y-Tech", "YTech"]),
    Company("Webify", ["Webify"]),

    # ---- Added 2026-09-29: more Jerusalem employers of designers ----
    # Tech (Har Hotzvim, Malha, Givat Ram)
    Company("Triple Whale", ["Triple Whale", "TripleWhale"],
            ("greenhouse", "triplewhale")),
    Company("Medinol", ["Medinol", "מדינול"],
            ("page", "https://medinol.com/en/working-in-medinol/")),
    Company("OrCam", ["OrCam", "אורקם"]),
    Company("Sight Diagnostics", ["Sight Diagnostics"]),
    Company("BrainsWay", ["BrainsWay", "בריינסוויי"]),
    Company("Alpha Tau", ["Alpha Tau", "אלפא טאו"]),
    Company("Teramount", ["Teramount"]),
    Company("BrainQ", ["BrainQ"]),
    Company("Ex Libris / Clarivate", ["Ex Libris", "Clarivate", "אקס ליבריס"]),
    Company("Oramed", ["Oramed", "אורמד"]),
    Company("Intel", ["Intel", "אינטל"]),
    # Hospitals and colleges
    Company("הדסה", ["הדסה", "Hadassah"],
            ("page", "https://he.hadassah.org.il/wanted/careers")),
    Company("שערי צדק", ["שערי צדק", "Shaare Zedek", "Shaarei Tzedek"]),
    Company("JCT - המרכז האקדמי לב", ["המרכז האקדמי לב", "Jerusalem College of Technology", "JCT"]),
    Company("מכללת עזריאלי", ["מכללת עזריאלי", "עזריאלי מכללה", "Azrieli College"],
            ("page", "https://www.jce.ac.il/possitions")),
    Company("המרכז האקדמי שלם", ["המרכז האקדמי שלם", "Shalem College"]),
    Company("מוסררה", ["מוסררה", "Musrara"]),
    # Museums and culture
    Company("הספרייה הלאומית", ["הספרייה הלאומית", "הספריה הלאומית", "National Library of Israel"]),
    Company("יד ושם", ["יד ושם", "Yad Vashem"]),
    Company("מוזיאון מגדל דוד", ["מגדל דוד", "Tower of David"]),
    Company("מוזיאון המדע בלומפילד", ["בלומפילד", "Bloomfield Science Museum"]),
    Company("מוזיאון ארצות המקרא", ["ארצות המקרא", "Bible Lands Museum"],
            ("page", "https://www.blmj.org/%D7%93%D7%A8%D7%95%D7%A9%D7%99%D7%9D/")),
    Company("סינמטק ירושלים", ["סינמטק ירושלים", "Jerusalem Cinematheque"]),
    Company("רשות העתיקות", ["רשות העתיקות", "Israel Antiquities Authority"]),
    # Public bodies and NGOs
    Company("עיריית ירושלים", ["עיריית ירושלים", "Jerusalem Municipality"]),
    Company("הרשות לפיתוח ירושלים", ["הרשות לפיתוח ירושלים", "Jerusalem Development Authority"]),
    Company("קרן ירושלים", ["קרן ירושלים", "Jerusalem Foundation"]),
    Company("הסוכנות היהודית", ["הסוכנות היהודית", "Jewish Agency"]),
    Company("קרן היסוד", ["קרן היסוד", "Keren Hayesod"]),
    Company("קק\"ל", ["קק\"ל", "קרן קיימת", "KKL", "JNF"]),
    Company("תגלית", ["תגלית", "Birthright Israel", "Taglit"]),
    Company("Nefesh B'Nefesh", ["Nefesh B'Nefesh", "Nefesh BNefesh", "נפש בנפש"],
            ("bamboohr", "nbn")),
    Company("המכון הישראלי לדמוקרטיה", ["המכון הישראלי לדמוקרטיה", "Israel Democracy Institute"],
            ("page", "https://www.idi.org.il/about/jobs/")),
    Company("ג'וינט ישראל", ["ג'וינט", "ג׳וינט", "JDC"],
            ("page", "https://thejoint.org.il/career/")),
    # Media and publishing
    Company("Jerusalem Post", ["Jerusalem Post", "ג'רוזלם פוסט"]),
    Company("Times of Israel", ["Times of Israel"]),
    Company("Gefen Publishing", ["Gefen Publishing"]),
    Company("Feldheim", ["Feldheim", "פלדהיים"]),

    # ---- Added 2026-10-11: Har Hotzvim park directory, Malha, Talpiot,
    # Givat Shaul and other Jerusalem employers ----
    # Har Hotzvim
    Company("Kramer Electronics", ["Kramer Electronics", "Kramer AV", "קרמר אלקטרוניקה"]),
    Company("Rafael", ["Rafael Advanced Defense", "Rafael", "רפאל"]),
    Company("Elbit Systems Rokar", ["Rokar", "רוקר", "Elbit Systems", "אלביט"]),
    Company("Altera", ["Altera"]),
    Company("KLA", ["KLA"]),
    Company("Kyocera AVX", ["Kyocera AVX", "KYOCERA AVX", "AVX"]),
    Company("Merck", ["Merck", "Sigma-Aldrich", "MilliporeSigma", "מרק"]),
    Company("Rafa Laboratories", ["Rafa Laboratories", "Rafa Labs", "מעבדות רפא"]),
    Company("Mapi Pharma", ["Mapi Pharma", "מאפי פארמה"]),
    Company("Izun Pharma", ["Izun Pharma", "Izun", "איזון פארמה"]),
    Company("Phibro Israel", ["Phibro", "פיברו"]),
    Company("Image Navigation", ["Image Navigation"]),
    Company("RenalSense", ["RenalSense"]),
    Company("Accellix", ["Accellix"]),
    Company("Stem Cell Medicine", ["Stem Cell Medicine"]),
    Company("Cross River", ["Cross River"]),
    Company("C2A Security", ["C2A Security", "C2A"]),
    Company("Lidwave", ["Lidwave"]),
    Company("Optimet", ["Optimet"]),
    Company("Accubeat", ["Accubeat", "AccuBeat"]),
    Company("Arjet Digital", ["Arjet"]),
    Company("Condor Pacific", ["Condor Pacific"]),
    Company("Copprint", ["Copprint"]),
    Company("BrightSource", ["BrightSource"]),
    Company("Solaris Synergy", ["Solaris Synergy"]),
    Company("RSIP Vision", ["RSIP Vision", "RSIP"]),
    Company("Correlor", ["Correlor"]),
    Company("Agat Software", ["Agat Software", "אגת"]),
    Company("OpenApp", ["OpenApp", "אופנאפ"]),
    Company("Clicktack", ["Clicktack", "קליקטאק"]),
    Company("Tide Technology", ["Tide Technology"]),
    Company("Oracle", ["Oracle", "אורקל"]),
    Company("Apple", ["Apple", "אפל"]),
    Company("IDT Global Israel", ["IDT"]),
    Company("Ness Technologies", ["Ness Technologies", "Ness Digital", "נס טכנולוגיות"]),
    Company("Bynet", ["Bynet", "בינת"]),
    Company("Sqlink", ["Sqlink", "אסקיולינק"]),
    Company("CityBook Services", ["CityBook", "סיטיבוק"]),
    Company("Hilma", ["Hilma", "הילמה", "הילמ\"ה"]),
    Company("Torah Live", ["Torah Live", "TorahLive"]),
    Company("HaPeles", ["הפלס"]),
    Company("לפ\"מ", ["לפ\"מ", "לשכת הפרסום הממשלתית"]),
    Company("מפעל הפיס", ["מפעל הפיס", "Mifal HaPais", "Pais"]),
    Company("משרד הבריאות", ["משרד הבריאות", "Ministry of Health"]),
    Company("חברת החשמל", ["חברת החשמל", "חברת חשמל", "Israel Electric"]),
    Company("Image College", ["מכללת אימג'", "מכללת אימג׳", "Image College"]),
    # Malha technology park
    Company("IBM", ["IBM"]),
    Company("Freightos", ["Freightos", "פרייטוס"]),
    Company("Kaspersky", ["Kaspersky", "קספרסקי"]),
    Company("מקור ראשון", ["מקור ראשון", "Makor Rishon"]),
    Company("רשות החדשנות", ["רשות החדשנות", "Israel Innovation Authority"]),
    Company("הרשות הלאומית לבטיחות בדרכים", ["הרשות הלאומית לבטיחות בדרכים", "Road Safety Authority"]),
    Company("גן החיות התנכי", ["גן החיות התנכי", "Biblical Zoo", "Jerusalem Zoo"]),
    # Talpiot
    Company("Kratos General Microwave", ["Kratos", "General Microwave", "קרטוס"]),
    Company("Sixdof Space", ["Sixdof", "6DOF Space"]),
    Company("DDS Security", ["DDS Security", "DDS"]),
    Company("Novamed", ["Novamed", "נובאמד"]),
    Company("AutoLeadStar / Impel", ["AutoLeadStar", "Impel"]),
    Company("רמי לוי", ["רמי לוי", "Rami Levy"]),
    # Givat Shaul, city centre and others
    Company("Cielo", ["Cielo Inertial", "סיאלו"]),
    Company("Dexcel Pharma", ["Dexcel", "דקסל פארמה"]),
    Company("Via", ["Via Transportation", "Ride with Via"]),
    Company("כאן - תאגיד השידור", ["תאגיד השידור", "כאן תאגיד", "Kan Broadcasting", "Israeli Public Broadcasting"]),
    Company("Mishpacha", ["Mishpacha", "מגזין משפחה"]),
    Company("מאפיות אנג'ל", ["אנג'ל", "אנג׳ל", "Angel Bakeries"]),
    Company("מאפיית ברמן", ["ברמן", "Berman Bakery"]),
    Company("מצות יהודה", ["מצות יהודה", "Yehuda Matzos"]),
    Company("Civan", ["Civan"]),
    Company("Atlas Sweets", ["Atlas Sweets", "אטלס מתוקים"]),
    Company("Microsoft", ["Microsoft", "מיקרוסופט"]),
    Company("Nvidia", ["NVIDIA", "Nvidia", "אנבידיה"]),
    Company("OurCrowd", ["OurCrowd"]),
    Company("VinciWorks", ["VinciWorks"]),
    Company("Rapaport", ["Rapaport"]),
    Company("Visionary.ai", ["Visionary.ai", "Visionary AI"]),
    Company("Sweetch", ["Sweetch"]),
    Company("Genetika+", ["Genetika"]),
    Company("יד שרה", ["יד שרה", "Yad Sarah"]),
    Company("ALYN", ["ALYN", "אלי\"ן", "אליין"]),
    Company("Shalva", ["Shalva", "שלוה", "שלווה"]),
    Company("Aish HaTorah", ["Aish HaTorah", "Aish", "אש התורה"]),
]
