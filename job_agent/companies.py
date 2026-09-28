"""Watch-list of Jerusalem companies (from Компании_по_районам_v4.xlsx).

Each company has:
- `aliases`: names (English/Hebrew) used to recognise the company on job
  boards (LinkedIn, AllJobs, Drushim, JobMaster). Matched as whole words
  against the vacancy's company name.
- `watch` (optional): how to check the company's own careers site daily:
    ("lever", "<company>")                     — Lever EU postings API
    ("greenhouse", "<board>")                  — Greenhouse board API
    ("workday", "<host>", "<tenant>", "<site>") — Workday jobs API
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
    Company("Nevelis", ["Nevelis"]),
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
    Company("Lightricks", ["Lightricks", "לייטריקס"],
            ("greenhouse", "lightricks")),
    Company("Yissum", ["Yissum", "יישום"]),
    Company("Alpha Omega", ["Alpha Omega", "אלפא אומגה"],
            ("page", "https://www.alphaomega-eng.com/Careers")),
    Company("Compumat", ["Compumat", "קומפומט"]),
    Company("Ajinomatrix", ["Ajinomatrix"]),
    # City centre, academia, government
    Company("מערך הסייבר הלאומי", ["מערך הסייבר", "National Cyber Directorate"]),
    Company("LeverageIT (illuminea)", ["illuminea", "LeverageIT", "Leverage IT"],
            ("page", "https://leverage.it/careers/")),
    Company("Bagel Studio", ["Bagel Studio"]),
    Company("Beyondesigns", ["Beyondesigns"]),
    Company("Atreo", ["Atreo"]),
    Company("Goldfish Marketing", ["Goldfish Marketing"]),
    Company("Dofinity", ["Dofinity", "דופיניטי"]),
    Company("Quickode", ["Quickode"]),
    Company("האוניברסיטה העברית", ["האוניברסיטה העברית", "Hebrew University", "HUJI"]),
    Company("בצלאל", ["בצלאל", "Bezalel"],
            ("page", "https://www.bezalel.ac.il/about/suppliers-tenders")),
    Company("מוזיאון ישראל", ["מוזיאון ישראל", "Israel Museum"]),
    # Suburbs
    Company("Say", ["Say Brand", "Say Studio"]),
    Company("Y-Tech", ["Y-Tech", "YTech"]),
    Company("Webify", ["Webify"]),
]
