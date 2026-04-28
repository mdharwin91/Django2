# from django.db import models

schoolInformation = {
    "schoolName": "Vasantham Nursery & Primary School",
    "place": "Maruthakulam",
    "trustName":"VASANTHAM EDUCATIONAL & CHARITABLE TRUST",
    "trustAddress": "1/227, Main Road, Maruthakulam, Tirunelveli 627151",
    "trustRegistrationNumber": "Reg No. 1/2024",
    "shotName": "Vasantham School",
    "schoolAddress": "1/293, Main Road, Maruthakulam, Tirunelveli 627151",
    "founder": "Late. Vasanthi J Princess Edwin",
    "vasantham": "VASANTHAM",
    "trustExt":"Educational & Charitable Trust",
    "nps": "Nursery & Primary School", 
    "trustEmail": "vasantham.ectrust@gmail.com",
    "trustMobile": "+91 94435 08833"
}

SchoolStandard = [
	('LKG', 'LKG'),
	('UKG', 'UKG'),
    ('I', 'I - STD'),
    ('II', 'II - STD'),
    ('III', 'III - STD'),
    ('IV', 'IV - STD'),
    ('V', 'V - STD')
]

Status = [
    ("Active", 'Active'),
    ("Inactive", 'Inactive')
]

free_edu = [
    ("YES", 'RTE/FC'),
    ("NO", 'NA')
]


profile = [
    ("Student", 'Student'),
    ("Teacher", 'Teacher'),
    ("Admin", 'Admin')
]
user = {
        "name": "empty_name",
        "dob": "dd/mm/yyyy",
        "doj": "dd/mm/yyyy",
        "std": "class_taking",
        "age": 0,
        "userProfile": "Teacher"
    }

sampleUser = {
    "name": "Dharwin M",
    "dob": "15/09/1991",
    "doj": "01/06/1994",
    "username": "dh",
    "password": "dh1",
    "std": "NA",
    "age": 32,
    "userProfile": "Admin",
    
}

term = {
    "term1": "Term 1",
    "term2": "Term 2",
    "term3": "Term 3"
}

feeNames = {
    "tuitionFee": "Tuition Fee",
    "libraryFee": "Library Fee",
    "sportsFee": "Sports Fee",
    "transportFee": "Transport Fee",
    "otherFee": "Other Fee",
    "admisionFee": "Admission Fee (NEW)",
    "miscFee": "Miscellaneous Fee",
    "specialFee": "Special Fee",
    "term1": "Term 1",
    "term2": "Term 2",
    "term3": "Term 3",
    "regisFee": "Registration Fee (NEW)"
}

bonafide_msg = {
    "Student": "This is to certify that [Name], [SID] ([EMIS No: ]), is a bonafide student of [School Name] studying in [Class] standard for the academic year [Year].",
    "Teacher": "This is to certify that [Name], [TID] ([EMIS No: ]) is a bonafide teacher at [School Name] since [Joining Date]."
}
    

# Create your models here.
