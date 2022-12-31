<?php
	$server = str_replace('?', '', "$_SERVER[REQUEST_URI]");
	header("Location: steam:/$server");
?>