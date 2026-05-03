CREATE DATABASE testdb;
GO
USE testdb;
GO
CREATE LOGIN [kafka] WITH PASSWORD=N'kafkatest' , DEFAULT_DATABASE=[testdb], CHECK_EXPIRATION=OFF, CHECK_POLICY=OFF;
GO
EXEC testdb..sp_addsrvrolemember @loginame= N'kafka', @rolename = N'sysadmin';
GO
CREATE TABLE testdb.dbo.Employee ( EmployeeID INT PRIMARY KEY, FirstName NVARCHAR(50) NOT NULL, LastName NVARCHAR(50) NOT NULL);
GO
EXEC sys.sp_cdc_enable_db;
GO
EXEC sys.sp_cdc_enable_table @source_schema = N'dbo', @source_name = N'Employee', @role_name = N'cdc_reader', @supports_net_changes = 0;
GO
EXEC sys.sp_cdc_help_change_data_capture;
GO
INSERT INTO testdb.dbo.Employee (EmployeeID, FirstName, LastName) VALUES (1, 'John', 'Doe');
INSERT INTO testdb.dbo.Employee (EmployeeID, FirstName, LastName) VALUES (2, 'Srinivas', 'Sahu');
GO
