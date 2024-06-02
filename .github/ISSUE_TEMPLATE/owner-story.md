---
name: Owner Story
about: Contact Us Feature
title: Creating contact us in landing page
---

**As a** Owner 
 **I need** to have a independent form contact us in my landing page website
 **So that** people can send their need and ask for in my platform
   
 ### Details and Assumptions
 * We creating our own independent form contact us without any plugin or third party
 * The customer data is not stored in other third party, instead in our database
   
 ### Acceptance Criteria  
   
 ```gherkin
 Given there is some user input their email, username and message
 When they are going to click the submit button
 Then the user data is going to send to our database
 ```
