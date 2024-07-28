<?php
$servername = "localhost";
$username = "root";
$password = "password";
$dbname = "test_db";

// Створення з'єднання
$conn = mysqli_connect($servername, $username, $password, $dbname);

// Перевірка з'єднання
if (!$conn) {
    die("Connection failed: " . mysqli_connect_error());
}
echo "Connected successfully";
?>
