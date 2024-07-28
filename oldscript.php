<?php
$servername = "localhost";
$username = "root";
$password = "password";
$dbname = "test_db";

// Створення з'єднання
$conn = mysql_connect($servername, $username, $password);

// Перевірка з'єднання
if (!$conn) {
    die('Could not connect: ' . mysql_error());
}
echo 'Connected successfully to ' . $dbname;
?>
