# Health-on-hands

##  Project Overview

**Health on Hands** is a web-based hospital management and doctor appointment booking platform designed for multispecialty hospitals. It streamlines online appointment booking, vaccination scheduling, and doctor-patient interactions. The system ensures user convenience, prevents slot overlaps, and supports accurate report uploads.

The platform includes **three modules**:

* **Hospital/Admin** – Manage doctors, nurses, vaccines, officers, and appointments.
* **Doctor** – Define availability, manage appointments, prescribe treatments, and upload reports.
* **Patient** – Register/login, book doctor or vaccine appointments, make payments, and track history.

---

## Features

* Role-based modules (**Admin, Doctor, Patient**)
* Doctor availability & **auto-scheduled 15-minute slots**
* Online **vaccination booking** with/without prescription requirement
* Real-time **slot blocking** to prevent double bookings
* **Secure payments** with transaction status tracking
* Prescription management & report uploads
* Appointment rescheduling & cancellation
* Patient history tracking (appointments, payments, prescriptions)

---

## 🛠Tech Stack

* **Frontend**: HTML, CSS, Bootstrap
* **Backend**: PHP
* **Database**: MySQL
* **Hosting**: AWS Cloud Services
* **Additional Tools**: XAMPP (local deployment)

---

## Database Design

The system uses **nine collections**:

* `Admin` – Login credentials, doctor & officer management
* `Doctor` – Profile, specialization, schedule, consultation fee
* `Patient` – Registration details, login, personal info
* `Officer` – Staff handling vaccinations
* `Vaccines` – Vaccine details, prescription requirement, availability
* `Time-slots` – Auto-generated 15-min slots per doctor availability
* `Appointment` – Booking details (patient, doctor, vaccine, status)
* `Prescription` – Doctor’s recommendations & treatment notes
* `Payment` – Card details, transaction records

---

## Screens & Workflows

* **Admin**: Manage officers, doctors, vaccines, slots
* **Doctor**: Login → View appointments → Prescribe → Manage slots
* **Patient**: Register/Login → Browse vaccines/doctors → Book appointment → Pay fees → View history

---

## Installation & Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/<your-username>/health-on-hands.git
   ```
2. Install [XAMPP](https://www.apachefriends.org/) and start **Apache & MySQL**.
3. Import the provided SQL file into MySQL.
4. Place the project files inside the `htdocs` folder.
5. Run the project locally:

   ```
   http://localhost/health-on-hands
   ```

---

## Future Enhancements

* Integration with **real-time notifications** (SMS/Email)
* AI-driven **doctor recommendation system**
* **Mobile app version** for Android/iOS
* Multi-language support for diverse users

---

 *This project was developed as part of our Master’s program to provide a scalable and user-friendly hospital appointment booking solution.*

---
