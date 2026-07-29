import pandas as pd
import requests
from datetime import datetime

class TickerDiscovery:
    @staticmethod
    def fetch_from_wikipedia() -> pd.DataFrame:
        """Fetch daftar saham IDX dari Wikipedia"""
        try:
            url = "https://en.wikipedia.org/wiki/List_of_companies_listed_on_the_Indonesia_Stock_Exchange"
            tables = pd.read_html(url)
            
            if tables:
                df = tables[0]
                df.columns = ["ticker", "name", "sector", "subsector", "listed_date"]
                df["ticker"] = df["ticker"].str.strip() + ".JK"
                df["is_active"] = True
                return df
            else:
                return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching from Wikipedia: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def fetch_static_extended() -> list:
        """Daftar ~300 saham likuid IDX"""
        tickers = [
            "BBRI.JK", "BBCA.JK", "TLKM.JK", "ASII.JK", "BMRI.JK", "UNVR.JK", "BBNI.JK",
            "INDF.JK", "GGRM.JK", "ICBP.JK", "KLBF.JK", "PTBA.JK", "ADRO.JK", "ANTM.JK",
            "INCO.JK", "SMGR.JK", "UNTR.JK", "MDKA.JK", "AMMN.JK", "PGAS.JK", "EXCL.JK",
            "ISAT.JK", "TPIA.JK", "CPIN.JK", "JPFA.JK", "AUTO.JK", "BRIS.JK", "MAPI.JK",
            "RALS.JK", "ERAA.JK", "HERO.JK", "LPPF.JK", "MPPA.JK", "AKRA.JK", "PETRA.JK",
            "ELTY.JK", "CTRA.JK", "BSDE.JK", "PWON.JK", "DUTI.JK", "NRCA.JK", "SSIA.JK",
            "WIKA.JK", "ADHI.JK", "PTPP.JK", "WSKT.JK", "TOTL.JK", "SMRA.JK", "CINT.JK",
            "DKFT.JK", "TINS.JK", "NICK.JK", "HRUM.JK", "GYPO.JK", "MBAP.JK", "PYFA.JK",
            "BTON.JK", "LOVE.JK", "EMTK.JK", "VIVA.JK", "KPIG.JK", "MTEL.JK", "FREN.JK",
            "DGIK.JK", "KBLV.JK", "MTDL.JK", "SLIS.JK", "BMSR.JK", "TOWR.JK", "ACES.JK",
            "RANC.JK", "SOSQ.JK", "WAPO.JK", "ARTO.JK", "BBYB.JK", "BBHI.JK", "BBMD.JK",
            "BBRK.JK", "BBKP.JK", "BBSI.JK", "BANK.JK", "BBTN.JK", "BDMN.JK", "BEKS.JK",
            "BJBR.JK", "BJTM.JK", "BLTZ.JK", "BNBA.JK", "BNBR.JK", "BNGA.JK", "BNII.JK",
            "BNLI.JK", "BPNL.JK", "BPRI.JK", "BSWA.JK", "BTPN.JK", "BTPS.JK", "BUMI.JK",
            "BYAN.JK", "CASH.JK", "CITA.JK", "CNKO.JK", "DEWA.JK", "DOID.JK", "ELSA.JK",
            "ENRG.JK", "ESIP.JK", "FAST.JK", "FIRE.JK", "GDST.JK", "GGRP.JK", "GHON.JK",
            "GIKO.JK", "GKON.JK", "GLVA.JK", "GOLT.JK", "GTBO.JK", "GZCO.JK", "HDFA.JK",
            "HEXA.JK", "HITS.JK", "HMSP.JK", "HOPE.JK", "IDPR.JK", "IFII.JK", "IGAR.JK",
            "IKAI.JK", "INAF.JK", "INCI.JK", "INDR.JK", "INKP.JK", "INPC.JK", "INPP.JK",
            "INTA.JK", "INTD.JK", "IPOL.JK", "IRRA.JK", "ITMA.JK", "JECC.JK", "JGLE.JK",
            "JKON.JK", "JPRS.JK", "JSPT.JK", "KAEF.JK", "KBRI.JK", "KDSI.JK", "KEEN.JK",
            "KIAS.JK", "KICI.JK", "KIJM.JK", "KKGI.JK", "KOBX.JK", "KOIN.JK", "KRAS.JK",
            "LABA.JK", "LCGP.JK", "LEAD.JK", "LION.JK", "LMSH.JK", "LPCK.JK", "LPII.JK",
            "LRNA.JK", "LSIP.JK", "LTLS.JK", "MABC.JK", "MAMI.JK", "MASA.JK", "MBSS.JK",
            "MCAS.JK", "MDRN.JK", "MEDC.JK", "MERK.JK", "META.JK", "MFIN.JK", "MICE.JK",
            "MIFI.JK", "MIKA.JK", "MKPI.JK", "MLBI.JK", "MLIA.JK", "MLPL.JK", "MNCN.JK",
            "MPMX.JK", "MRAT.JK", "MREI.JK", "MYOH.JK", "MYOR.JK", "MYTX.JK", "NELY.JK",
            "NIPS.JK", "NISP.JK", "NOBU.JK", "NSFC.JK", "NTBK.JK", "OASA.JK", "OCAP.JK",
            "OKAS.JK", "OMRE.JK", "PADI.JK", "PALM.JK", "PANI.JK", "PANS.JK", "PEAT.JK",
            "PEGY.JK", "PEST.JK", "PFIS.JK", "PGLI.JK", "PJAA.JK", "PKPK.JK", "PLIN.JK",
            "PNBS.JK", "PNIN.JK", "PNLF.JK", "POLA.JK", "POLU.JK", "PPGL.JK", "PPRI.JK",
            "PRES.JK", "PRIM.JK", "PSAB.JK", "PSDN.JK", "PTPS.JK", "PTRO.JK", "PUDP.JK",
            "PUJA.JK", "RALF.JK", "RDTX.JK", "RELI.JK", "RIGG.JK", "ROBA.JK", "SAGE.JK",
            "SAME.JK", "SAPX.JK", "SCMA.JK", "SCPI.JK", "SDMU.JK", "SDPC.JK", "SDRA.JK",
            "SGRO.JK", "SIAP.JK", "SICO.JK", "SIMA.JK", "SINT.JK", "SKBM.JK", "SKLT.JK",
            "SKRN.JK", "SKYB.JK", "SMAR.JK", "SMBR.JK", "SMDM.JK", "SMDR.JK", "SMKL.JK",
            "SMMT.JK", "SMRU.JK", "SMSM.JK", "SONA.JK", "SPMA.JK", "SQMI.JK", "SRSN.JK",
            "STAA.JK", "STAR.JK", "STTP.JK", "SUGI.JK", "SULI.JK", "SUPR.JK", "SWAT.JK",
            "TALA.JK", "TAMA.JK", "TARA.JK", "TAXI.JK", "TFCO.JK", "TGKA.JK", "TIRA.JK",
            "TKIM.JK", "TRAM.JK", "TRIL.JK", "TRIM.JK", "TRIO.JK", "TRST.JK", "TRUE.JK",
            "TSPC.JK", "ULTJ.JK", "UNIT.JK", "UNSP.JK", "VOKS.JK", "WEGE.JK", "WICO.JK",
            "WINS.JK", "WIRG.JK", "YPAS.JK", "YULE.JK"
        ]
        return tickers
    
    @staticmethod
    def save_to_db(db) -> int:
        """Simpan ticker ke database"""
        tickers = TickerDiscovery.fetch_static_extended()
        count = 0
        
        for ticker in tickers:
            try:
                with db._connect() as conn:
                    conn.execute("""
                        INSERT INTO stocks (ticker, is_active)
                        VALUES (?, 1)
                        ON CONFLICT (ticker) DO NOTHING
                    """, (ticker,))
                    conn.commit()
                    count += 1
            except:
                pass
        
        return count
