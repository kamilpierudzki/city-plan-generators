from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import print_list_str
from transit_agencies.gzm_ztm import GzmZtm
from transit_agencies.km_kolobrzeg import KmKolobrzeg
from transit_agencies.m_czestochowa import MCzestochowa
from transit_agencies.mpk_bialystok import MpkBialystok
from transit_agencies.mpk_krakow import MpkKrakow
from transit_agencies.mpk_lodz import MpkLodz
from transit_agencies.mpk_poznan import MpkPoznan
from transit_agencies.mpk_swidnica import MpkSwidnica
from transit_agencies.mpk_wroclaw import MpkWroclaw
from transit_agencies.mzk_bielsko_biala import MzkBielskoBiala
from transit_agencies.wtp_warszawa import WtpWarszawa
from transit_agencies.zdmikp_bydgoszcz import ZdmikpBydgoszcz
from transit_agencies.zdtm_szczecin import ZdtmSzczecin
from transit_agencies.zdzit_olsztyn import ZdzitOlsztyn
from transit_agencies.zim_slupsk import ZimSlupsk
from transit_agencies.ztm_gdansk import ZtmGdansk
from transit_agencies.ztm_lublin import ZtmLublin

if __name__ == '__main__':
    transit_agencies: list[TransitAgency] = [
        GzmZtm(),
        KmKolobrzeg(),
        MCzestochowa(),
        MpkBialystok(),
        MpkKrakow(),
        MpkLodz(),
        MpkPoznan(),
        MpkSwidnica(),
        MpkWroclaw(),
        MzkBielskoBiala(),
        WtpWarszawa(),
        ZdmikpBydgoszcz(),
        ZdtmSzczecin(),
        ZdzitOlsztyn(),
        ZimSlupsk(),
        ZtmGdansk(),
        ZtmLublin(),
    ]
    for transit_agency in transit_agencies:
        transit_agency.generate_data()

    print("---")
    for transit_agency in transit_agencies:
        print_list_str(transit_agency.get_transit_agency_name(), transit_agency.errors)
