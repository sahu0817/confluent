DECLARE @agent NVARCHAR(512);

SELECT @agent = COALESCE(N'SQLAgent$' + CONVERT(SYSNAME, SERVERPROPERTY('InstanceName')),
  N'SQLServerAgent');

EXEC master.dbo.xp_servicecontrol 'QueryState', @agent;
