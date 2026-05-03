# DJANGO

# SchoolBill - A Comprehensive School Management System
SchoolBill is a powerful and user-friendly school management system built with Django. It offers a wide range of features to streamline administrative tasks, enhance communication, and improve overall efficiency in educational institutions.

## Features
- **Student Management**: Easily manage student records, including enrollment, attendance, and academic performance
- **Teacher Management**: Keep track of teacher information, schedules, and performance evaluations
- **Class Management**: Organize classes, assign teachers, and manage class schedules
- **Fee Management**: Handle fee collection, generate invoices, and track payment history
- **Communication Tools**: Facilitate communication between teachers, students, and parents through messaging
- **Reporting and Analytics**: Generate detailed reports on various aspects of school operations for informed decision-making
## Installation

## Features to be added
1. Need to fix navig bar height( overlapping with below content) [FIXED]
2. possibilities for push notification [NOT FEASIBLE]
3. Add more features to admin panel [IN PROGRESS]
4. Add 2FA for change password. [ADDED]
5. Do Minification and Obfuscation. But make sure to keep the Feature, Style and Alignment undisturbed.[ADDED]
6. On the Bill Adjustment page, when the Student Bill is previewed on the right side, Make Bill No. Non Editable [FIXED]
7. Add Designation (Dropdown Selection) to Teacher and Admin profile, use options from designation on Models.py. Add necessery code to add this field in DB [ADDED]
8. Add a dropdown near to Parents Name Textbox with options as (Father, Mother, Gaudrian). so that its saves to DB as <FatherName> (Father) if father is selected. [ADDED]
9. Add feature to note the bugs while testing in Mobile. [ADDED]
10. Welcome message on the commons page is not visible clearly on Light theme. Make it theme aware [FIXED]
11. navig2 and secondary headers are not visible in mobile for Common, Teacher, Adminpage. [FIXED]
12. Increase the Font size of the username and password text boxes to match the 6 digit code box font size. Also adjust the width of the Textbox for mobile view compatible [FIXED]
13. Header in Login and Common looks different. Font size of title name is perfect in Login page header. but in common, teacher adminpage it looks small. [FIXED]
14. navigation bar is hiding behind the header on mobile view. fix it to visible even if we scroll down. [FIXED]
15. in Login page: on the mobile view make sure the navigation.html is after the header.html [FIXED]
16. Navigation bar only half visible on mobile view, brought further down to fully clear the header. [FIXED]
17. While on Mobile view, fix the visual gap between navig2 and secondary nav bar. [FIXED]
18. Place this logout on admipage right after the Header2.html. [FIXED]
19. There is a small gap between navig2 and secondary-nav bar on desktop view, analysis and fix [FIXED]
20. Extract Assets: Move all minified inline JavaScript and CSS into dedicated .js and .css files served via Django's static files.

## Coding Guidelines & Security
- **Secured Website & Zero Vulnerability:** Ensure all code adheres to strict security practices to prevent potential vulnerabilities (e.g., XSS, CSRF, SQLi).
- **Secure Routing:** Do not use easily guessable paths or endpoints for sensitive administrative or data-fetching actions.
- **Code Minification & Obfuscation:** Ensure frontend code (JavaScript/CSS) is minified and lightly obfuscated where applicable to protect logic and reduce payload size.
- **Consistency:** Always maintain the existing Format, Features, and Style of the application across all components when adding updates.
- **Theme Awareness:** Make all UI components Light/Dark theme aware.
- **Responsive Design:** Ensure design style is compatible with and optimized for both Mobile and Desktop Views.
- **View Awareness:** Make sure to keep the Desktop view undisturbed while fixing Mobile view and keep the mobile View undisturbed while fixing Desktop view.