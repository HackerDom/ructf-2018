# Eloquent
There is a DOM Based XSS in a web server, written with in-page javascript execution.
##### Syntax and logical mistakes
Because of wrong comparing and setting in javascript-file `static/js/frontend.js:106-118` when creating an article we can assign any value with prefix `'Current title:'` to the object with id=`mid-text` (in navigation bar). And it will be built into the html-page.
##### Attack
Using logical bug we can inject a html tag `<script>...</script>`. Possible way do it is using markdown syntax for create link inside an article. Doing requests to the other hosts is forbidden by CORS policy. It means, that we must do request to the out host. For example, we can write script, which build and submit html-form with a private suggestion to ourself with any information from the page (cookies in this case). All markdown text generates into html with some escaping, but it overcomes with adding javascript variables.

##### Defense
Just fix the logical bug.
