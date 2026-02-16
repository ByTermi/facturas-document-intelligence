/****** Object:  Table [dbo].[Factura]    Script Date: 03/02/2026 14:27:51 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Factura](
	[id_factura] [bigint] IDENTITY(1,1) NOT NULL,
	[CorreoAlumno] [varchar](100) NOT NULL,
	[Nombrefichero] [varchar](100) NOT NULL,
	[NumFactura] [varchar](50) NOT NULL,
	[FechaFactura] [smalldatetime] NOT NULL,
	[Cliente] [varchar](max) NOT NULL,
	[NIF cliente] [varchar](20) NOT NULL,
	[Comercializadora] [varchar](100) NOT NULL,
	[NIF comercializadora] [varchar](20) NOT NULL,
	[Diercción cliente] [varchar](150) NOT NULL,
	[Población cliente] [varchar](100) NULL,
	[Provincia cliente] [varchar](50) NULL,
	[CP cliente] [varchar](5) NULL,
	[Tarifa] [varchar](10) NULL,
	[Potencia contratada kW P1] [decimal](18, 2) NULL,
	[Potencia contratada kW P2] [decimal](18, 2) NULL,
	[Potencia contratada kW P3] [decimal](18, 2) NULL,
	[Potencia contratada kW P4] [decimal](18, 2) NULL,
	[Potencia contratada kW P5] [decimal](18, 2) NULL,
	[Potencia contratada kW P6] [decimal](18, 2) NULL,
	[Días factura] [smallint] NULL,
	[Precio P1 kW/día] [decimal](18, 2) NULL,
	[Precio P2 kW/día] [decimal](18, 2) NULL,
	[Precio P3 kW/día] [decimal](18, 2) NULL,
	[Precio P4 kW/día] [decimal](18, 2) NULL,
	[Precio P5 kW/día] [decimal](18, 2) NULL,
	[Precio P6 kW/día] [decimal](18, 2) NULL,
	[Precio E1 kWh] [decimal](18, 2) NULL,
	[Precio E2 kWh] [decimal](18, 2) NULL,
	[Precio E3 kWh] [decimal](18, 2) NULL,
	[Precio E4 kWn] [decimal](18, 2) NULL,
	[Precio E5 kWh] [decimal](18, 2) NULL,
	[Precio E6 kWh] [decimal](18, 2) NULL,
	[Consumo P1 kWh] [int] NULL,
	[Consumo P2 kWh] [int] NULL,
	[Consumo P3 kWh] [int] NULL,
	[Consumo P4 kWh] [int] NULL,
	[Consumo P5 kWh] [int] NULL,
	[Consumo P6 kWh] [int] NULL,
	[Base imponible] [decimal](18, 2) NULL,
	[TipoFactura] [varchar](10) NULL,
	[CUPS] [varchar](100) NULL,
	[Contrato] [varchar](50) NULL,
 CONSTRAINT [PK_Factura] PRIMARY KEY CLUSTERED 
(
	[id_factura] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Luz/Gas' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'Factura', @level2type=N'COLUMN',@level2name=N'TipoFactura'
GO

