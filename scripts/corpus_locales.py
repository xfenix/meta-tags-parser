"""Localized copy used to build the synthetic real-world HTML corpus.

Every entry mimics the wording real sites of that language use in their meta tags: news headlines,
marketing descriptions, article paragraphs and keyword lists. The content is deliberately plain text
so it can also be encoded into the legacy single/multi byte charsets listed in ``legacy_encoding``.
"""

import dataclasses
import types
import typing


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class LocaleContent:
    """Everything the corpus generator needs to write one page in a single language."""

    language_code: str
    locale_code: str
    site_domain: str
    site_title: str
    headlines: tuple[str, ...]
    descriptions: tuple[str, ...]
    paragraphs: tuple[str, ...]
    keyword_list: tuple[str, ...]
    author_names: tuple[str, ...]
    section_names: tuple[str, ...]
    text_direction: str = "ltr"
    legacy_encoding: str | None = None


ALL_LOCALES: typing.Final[typing.Mapping[str, LocaleContent]] = types.MappingProxyType(
    {
        "ru": LocaleContent(
            language_code="ru",
            locale_code="ru_RU",
            site_domain="novosti-portal.ru",
            site_title="Новости и аналитика",
            headlines=(
                "Учёные описали новый способ хранения энергии в перовскитных элементах",
                "Городские власти представили план реконструкции набережной",
                "Рынок труда в ИТ: зарплаты выросли на 12 процентов за год",
                "Как выбрать велосипед для города: подробное руководство",
            ),
            descriptions=(
                "Подробный разбор ситуации с комментариями экспертов отрасли и открытыми данными.",
                "Что изменится для жителей, сколько это стоит и когда закончатся работы.",
                "Большое исследование рынка: цифры, графики и прогноз на следующий год.",
            ),
            paragraphs=(
                "По словам исследователей, новая технология позволяет увеличить плотность энергии "
                "почти вдвое при сопоставимой стоимости производства.",
                "Представители профильного ведомства подчеркнули, что окончательное решение будет "
                "принято после общественных слушаний и экспертизы проекта.",
                "Аналитики отмечают, что спрос смещается в сторону специалистов среднего уровня, "
                "тогда как число вакансий для новичков сокращается третий квартал подряд.",
                "Редакция собрала мнения читателей и подготовила краткую инструкцию для тех, "
                "кто планирует покупку в ближайшие месяцы.",
            ),
            keyword_list=("новости", "аналитика", "технологии", "город", "экономика", "исследование"),
            author_names=("Анна Ковалёва", "Дмитрий Соколов", "Мария Ершова"),
            section_names=("Технологии", "Город", "Экономика", "Общество"),
            legacy_encoding="windows-1251",
        ),
        "en": LocaleContent(
            language_code="en",
            locale_code="en_US",
            site_domain="dailyexaminer.com",
            site_title="The Daily Examiner",
            headlines=(
                "Researchers Report a Cheaper Way to Store Grid Scale Energy",
                "City Council Approves the Waterfront Redevelopment Plan",
                "Software Salaries Climbed Twelve Percent Over the Past Year",
                "How to Pick a Commuter Bike Without Overpaying",
            ),
            descriptions=(
                "An in depth look at the numbers, with commentary from people who work in the field.",
                "What changes for residents, how much it costs and when the work is expected to finish.",
                "A full market survey with charts, raw data and a forecast for the coming year.",
            ),
            paragraphs=(
                "The team says the approach roughly doubles energy density while keeping the "
                "manufacturing cost close to what existing cells require today.",
                "Officials stressed that nothing is final until the public hearings wrap up and the "
                "independent review board signs off on the proposal.",
                "Analysts point out that demand keeps shifting toward mid level engineers while "
                "entry level postings have shrunk for a third consecutive quarter.",
                "We collected reader questions and turned them into a short buying guide for anyone "
                "planning a purchase in the next few months.",
            ),
            keyword_list=("news", "analysis", "technology", "city", "economy", "research"),
            author_names=("Laura Whitfield", "Marcus Bell", "Priya Raghunathan"),
            section_names=("Technology", "City", "Business", "Culture"),
            legacy_encoding="iso-8859-1",
        ),
        "de": LocaleContent(
            language_code="de",
            locale_code="de_DE",
            site_domain="tagesbericht.de",
            site_title="Tagesbericht",
            headlines=(
                "Forscher stellen günstigere Speicherzellen für das Stromnetz vor",
                "Stadtrat beschließt den Umbau der Uferpromenade",
                "Gehälter in der Softwarebranche steigen um zwölf Prozent",
                "Welches Fahrrad für den Arbeitsweg wirklich taugt",
            ),
            descriptions=(
                "Eine ausführliche Einordnung mit Zahlen und Stimmen aus der Branche.",
                "Was sich für die Anwohner ändert, was es kostet und wann die Arbeiten enden.",
                "Große Marktübersicht mit Grafiken, Rohdaten und einer Prognose für das nächste Jahr.",
            ),
            paragraphs=(
                "Nach Angaben des Teams verdoppelt das Verfahren die Energiedichte nahezu, "
                "ohne die Herstellungskosten nennenswert zu erhöhen.",
                "Die Behörde betonte, dass eine endgültige Entscheidung erst nach der "
                "Bürgerbeteiligung und der Prüfung durch Sachverständige fällt.",
                "Fachleute beobachten eine Verschiebung hin zu erfahrenen Entwicklern, während "
                "Einstiegsstellen im dritten Quartal in Folge zurückgehen.",
                "Wir haben Leserfragen gesammelt und daraus einen kompakten Kaufratgeber gemacht.",
            ),
            keyword_list=("nachrichten", "analyse", "technik", "stadt", "wirtschaft"),
            author_names=("Katrin Vogelsang", "Jonas Brehmer", "Sabine Lindqvist"),
            section_names=("Technik", "Stadt", "Wirtschaft", "Kultur"),
            legacy_encoding="iso-8859-1",
        ),
        "fr": LocaleContent(
            language_code="fr",
            locale_code="fr_FR",
            site_domain="lejournalquotidien.fr",
            site_title="Le Journal Quotidien",
            headlines=(
                "Des chercheurs proposent un stockage d'énergie moins coûteux",
                "Le conseil municipal valide la rénovation des quais",
                "Les salaires du logiciel progressent de douze pour cent",
                "Comment choisir un vélo urbain sans se ruiner",
            ),
            descriptions=(
                "Une analyse détaillée, chiffres à l'appui, avec les acteurs du secteur.",
                "Ce qui change pour les riverains, le coût du projet et le calendrier des travaux.",
                "Une étude complète du marché avec des données brutes et des prévisions.",
            ),
            paragraphs=(
                "Selon l'équipe, le procédé double presque la densité énergétique sans augmenter "
                "sensiblement le coût de fabrication des cellules.",
                "L'administration rappelle qu'aucune décision ne sera prise avant la fin de la "
                "consultation publique et l'avis des experts indépendants.",
                "Les analystes constatent un glissement vers les profils confirmés alors que les "
                "offres destinées aux débutants reculent pour le troisième trimestre.",
                "Nous avons rassemblé les questions des lecteurs pour en tirer un guide d'achat.",
            ),
            keyword_list=("actualités", "analyse", "technologie", "ville", "économie"),
            author_names=("Camille Brissot", "Étienne Marchal", "Naïma Dubourg"),
            section_names=("Technologie", "Ville", "Économie", "Culture"),
            legacy_encoding="iso-8859-1",
        ),
        "es": LocaleContent(
            language_code="es",
            locale_code="es_ES",
            site_domain="eldiarioabierto.es",
            site_title="El Diario Abierto",
            headlines=(
                "Investigadores presentan un almacenamiento de energía más barato",
                "El ayuntamiento aprueba la reforma del paseo marítimo",
                "Los sueldos del sector del software suben un doce por ciento",
                "Cómo elegir una bicicleta urbana sin gastar de más",
            ),
            descriptions=(
                "Un análisis a fondo con cifras y opiniones de quienes trabajan en el sector.",
                "Qué cambia para los vecinos, cuánto cuesta y cuándo terminan las obras.",
                "Un estudio completo del mercado con datos abiertos y previsiones para el año.",
            ),
            paragraphs=(
                "Según el equipo, el método casi duplica la densidad energética sin encarecer "
                "de forma apreciable la fabricación de las celdas.",
                "La administración insiste en que no habrá decisión definitiva hasta que acabe "
                "el periodo de consulta y llegue el informe de los peritos.",
                "Los analistas observan un desplazamiento hacia perfiles con experiencia mientras "
                "las ofertas de entrada caen por tercer trimestre consecutivo.",
                "Hemos reunido las preguntas de los lectores en una guía de compra breve.",
            ),
            keyword_list=("noticias", "análisis", "tecnología", "ciudad", "economía"),
            author_names=("Lucía Ferrán", "Gonzalo Estévez", "Marta Iriarte"),
            section_names=("Tecnología", "Ciudad", "Economía", "Cultura"),
            legacy_encoding="iso-8859-1",
        ),
        "pt": LocaleContent(
            language_code="pt-BR",
            locale_code="pt_BR",
            site_domain="folhaaberta.com.br",
            site_title="Folha Aberta",
            headlines=(
                "Pesquisadores apresentam armazenamento de energia mais barato",
                "Câmara aprova a reforma da orla da cidade",
                "Salários em software sobem doze por cento no ano",
                "Como escolher uma bicicleta urbana sem gastar demais",
            ),
            descriptions=(
                "Uma análise detalhada com números e depoimentos de quem trabalha no setor.",
                "O que muda para os moradores, quanto custa e quando as obras terminam.",
                "Levantamento completo do mercado com dados abertos e projeções para o ano.",
            ),
            paragraphs=(
                "Segundo a equipe, o método quase dobra a densidade de energia sem elevar de "
                "maneira significativa o custo de fabricação das células.",
                "O órgão responsável reforçou que nada será decidido antes do fim da consulta "
                "pública e do parecer técnico independente.",
                "Analistas veem uma migração para profissionais experientes enquanto as vagas de "
                "entrada caem pelo terceiro trimestre seguido.",
                "Reunimos as dúvidas dos leitores e transformamos tudo em um guia de compra.",
            ),
            keyword_list=("notícias", "análise", "tecnologia", "cidade", "economia"),
            author_names=("Renata Quadros", "Tiago Vilarinho", "Bruna Sampaio"),
            section_names=("Tecnologia", "Cidade", "Economia", "Cultura"),
            legacy_encoding="iso-8859-1",
        ),
        "it": LocaleContent(
            language_code="it",
            locale_code="it_IT",
            site_domain="corrieredelgiorno.it",
            site_title="Corriere del Giorno",
            headlines=(
                "Ricercatori propongono un accumulo di energia meno costoso",
                "Il consiglio comunale approva il rifacimento del lungomare",
                "Gli stipendi nel software crescono del dodici per cento",
                "Come scegliere una bici da città senza spendere troppo",
            ),
            descriptions=(
                "Un'analisi approfondita con numeri e voci di chi lavora nel settore.",
                "Che cosa cambia per i residenti, quanto costa e quando finiscono i lavori.",
                "Uno studio completo del mercato con dati aperti e previsioni per l'anno.",
            ),
            paragraphs=(
                "Secondo il gruppo di ricerca il metodo raddoppia quasi la densità energetica "
                "senza far salire in modo sensibile i costi di produzione.",
                "L'amministrazione ribadisce che nessuna decisione sarà presa prima della fine "
                "della consultazione pubblica e della perizia indipendente.",
                "Gli analisti registrano uno spostamento verso profili esperti mentre le offerte "
                "per chi inizia calano da tre trimestri.",
                "Abbiamo raccolto le domande dei lettori e ne abbiamo ricavato una guida.",
            ),
            keyword_list=("notizie", "analisi", "tecnologia", "città", "economia"),
            author_names=("Giulia Ferretti", "Alessio Marconi", "Chiara Bonfanti"),
            section_names=("Tecnologia", "Città", "Economia", "Cultura"),
            legacy_encoding="iso-8859-1",
        ),
        "pl": LocaleContent(
            language_code="pl",
            locale_code="pl_PL",
            site_domain="dziennikmiejski.pl",
            site_title="Dziennik Miejski",
            headlines=(
                "Naukowcy pokazali tańszy sposób magazynowania energii",
                "Rada miasta zatwierdziła przebudowę bulwarów",
                "Wynagrodzenia w branży oprogramowania wzrosły o dwanaście procent",
                "Jak wybrać rower miejski i nie przepłacić",
            ),
            descriptions=(
                "Szczegółowa analiza z liczbami i komentarzami osób z branży.",
                "Co zmieni się dla mieszkańców, ile to kosztuje i kiedy skończą się prace.",
                "Pełny przegląd rynku z otwartymi danymi i prognozą na przyszły rok.",
            ),
            paragraphs=(
                "Zdaniem zespołu metoda niemal podwaja gęstość energii, nie podnosząc przy tym "
                "znacząco kosztów produkcji ogniw.",
                "Urząd podkreśla, że ostateczna decyzja zapadnie dopiero po konsultacjach "
                "społecznych i opinii niezależnych ekspertów.",
                "Analitycy zauważają przesunięcie w stronę doświadczonych programistów, podczas "
                "gdy ofert dla początkujących ubywa trzeci kwartał z rzędu.",
                "Zebraliśmy pytania czytelników i przygotowaliśmy krótki poradnik zakupowy.",
            ),
            keyword_list=("wiadomości", "analiza", "technologia", "miasto", "gospodarka"),
            author_names=("Katarzyna Wrzosek", "Michał Dąbrowa", "Ewa Truszczyńska"),
            section_names=("Technologia", "Miasto", "Gospodarka", "Kultura"),
            legacy_encoding="iso-8859-2",
        ),
        "uk": LocaleContent(
            language_code="uk",
            locale_code="uk_UA",
            site_domain="miskyvisnyk.ua",
            site_title="Міський вісник",
            headlines=(
                "Науковці показали дешевший спосіб зберігання енергії",
                "Міська рада ухвалила реконструкцію набережної",
                "Зарплати в розробці програм зросли на дванадцять відсотків",
                "Як обрати міський велосипед і не переплатити",
            ),
            descriptions=(
                "Докладний розбір із цифрами та коментарями фахівців галузі.",
                "Що зміниться для мешканців, скільки коштує і коли завершать роботи.",
                "Повний огляд ринку з відкритими даними та прогнозом на наступний рік.",
            ),
            paragraphs=(
                "За словами дослідників, метод майже подвоює щільність енергії, майже не "
                "збільшуючи собівартість виробництва елементів.",
                "У відомстві наголосили, що остаточне рішення ухвалять лише після громадських "
                "слухань та висновку незалежних експертів.",
                "Аналітики фіксують зміщення попиту до досвідчених розробників, тоді як вакансій "
                "для початківців меншає третій квартал поспіль.",
                "Ми зібрали запитання читачів і зробили з них короткий посібник для покупців.",
            ),
            keyword_list=("новини", "аналітика", "технології", "місто", "економіка"),
            author_names=("Оксана Гриценко", "Богдан Ліщук", "Надія Кравець"),
            section_names=("Технології", "Місто", "Економіка", "Суспільство"),
            legacy_encoding="windows-1251",
        ),
        "tr": LocaleContent(
            language_code="tr",
            locale_code="tr_TR",
            site_domain="gunlukhaber.com.tr",
            site_title="Günlük Haber",
            headlines=(
                "Araştırmacılar daha ucuz bir enerji depolama yöntemi tanıttı",
                "Belediye meclisi sahil düzenlemesini onayladı",
                "Yazılım sektöründe maaşlar yüzde on iki arttı",
                "Şehir içi bisiklet seçerken nelere dikkat etmeli",
            ),
            descriptions=(
                "Sektörde çalışanların yorumlarıyla birlikte ayrıntılı bir değerlendirme.",
                "Mahalle sakinleri için ne değişiyor, maliyeti ne kadar ve işler ne zaman bitiyor.",
                "Açık verilerle hazırlanmış kapsamlı pazar araştırması ve yıllık öngörüler.",
            ),
            paragraphs=(
                "Ekibe göre yöntem, üretim maliyetini belirgin biçimde artırmadan enerji "
                "yoğunluğunu neredeyse ikiye katlıyor.",
                "İlgili kurum, kamuoyu görüşmeleri ve bağımsız bilirkişi raporu tamamlanmadan "
                "kesin bir karar verilmeyeceğini vurguladı.",
                "Analistler talebin deneyimli geliştiricilere kaydığını, giriş seviyesi ilanların "
                "ise üst üste üçüncü çeyrekte azaldığını belirtiyor.",
                "Okur sorularını topladık ve kısa bir satın alma rehberine dönüştürdük.",
            ),
            keyword_list=("haber", "analiz", "teknoloji", "şehir", "ekonomi"),
            author_names=("Elif Doğanay", "Kerem Aksoy", "Selin Batur"),
            section_names=("Teknoloji", "Şehir", "Ekonomi", "Kültür"),
            legacy_encoding="iso-8859-9",
        ),
        "ja": LocaleContent(
            language_code="ja",
            locale_code="ja_JP",
            site_domain="asahi-shimin.jp",
            site_title="朝日市民ニュース",
            headlines=(
                "研究チームが安価な系統用蓄電技術を発表",
                "市議会が海沿い遊歩道の再整備計画を承認",
                "ソフトウェア職の給与が前年比十二パーセント上昇",
                "通勤用自転車の選び方と価格の目安",
            ),
            descriptions=(
                "業界関係者の証言と公開データをもとにした詳細な分析記事です。",
                "住民にとって何が変わるのか、費用と工期をわかりやすく整理しました。",
                "図表と生データを添えた市場調査レポートと来年度の見通しです。",
            ),
            paragraphs=(
                "研究チームによると、この手法は製造費をほとんど増やさずにエネルギー密度をおよそ二倍にできるという。",
                "担当部局は、住民説明会と第三者による審査が終わるまで最終決定はしないと強調した。",
                "需要は中堅技術者へ移りつつあり、未経験者向けの求人は三四半期連続で減少している。",
                "読者から寄せられた質問をまとめ、購入前に確認したい点を短くまとめた。",
            ),
            keyword_list=("ニュース", "分析", "技術", "都市", "経済"),
            author_names=("田中 彩", "佐藤 健一", "鈴木 美咲"),
            section_names=("テクノロジー", "都市", "経済", "文化"),
            legacy_encoding="shift_jis",
        ),
        "zh": LocaleContent(
            language_code="zh-CN",
            locale_code="zh_CN",
            site_domain="chengshiribao.cn",
            site_title="城市日报",
            headlines=(
                "研究团队发布成本更低的电网储能方案",
                "市议会通过滨江步道改造计划",
                "软件行业薪资同比上涨百分之十二",
                "如何挑选一辆合适的通勤自行车",
            ),
            descriptions=(
                "结合行业从业者的说法与公开数据的深度分析报道。",
                "居民生活会有哪些变化，工程造价多少，何时完工。",
                "附有图表与原始数据的完整市场调查以及明年预测。",
            ),
            paragraphs=(
                "研究人员表示，这一方法几乎将能量密度提高一倍，而制造成本基本保持不变。",
                "主管部门强调，在公众听证与独立评审结束之前不会做出最终决定。",
                "分析人士指出，需求正在向中级工程师转移，面向新人的岗位已连续三个季度减少。",
                "我们整理了读者提出的问题，写成一份简短的选购指南。",
            ),
            keyword_list=("新闻", "分析", "科技", "城市", "经济"),
            author_names=("王丽娜", "陈志远", "刘晓彤"),
            section_names=("科技", "城市", "经济", "文化"),
            legacy_encoding="gbk",
        ),
        "ko": LocaleContent(
            language_code="ko",
            locale_code="ko_KR",
            site_domain="dosinews.co.kr",
            site_title="도시뉴스",
            headlines=(
                "연구진, 더 저렴한 계통 저장 기술 공개",
                "시의회, 해안 산책로 재정비 계획 승인",
                "소프트웨어 직군 임금 전년 대비 12퍼센트 상승",
                "출퇴근용 자전거 고르는 방법과 가격 기준",
            ),
            descriptions=(
                "업계 종사자의 설명과 공개 자료를 바탕으로 한 심층 분석 기사입니다.",
                "주민에게 무엇이 달라지는지, 비용과 공사 기간을 정리했습니다.",
                "도표와 원자료를 포함한 시장 조사와 내년 전망입니다.",
            ),
            paragraphs=(
                "연구진은 이 방식이 제조 비용을 거의 늘리지 않으면서 에너지 밀도를 두 배 가까이 높인다고 밝혔다.",
                "관계 부처는 주민 설명회와 독립 심사가 끝나기 전에는 최종 결정을 내리지 않겠다고 강조했다.",
                "분석가들은 수요가 중급 개발자로 옮겨가는 반면 신입 채용은 세 분기 연속 줄었다고 지적한다.",
                "독자들이 보내온 질문을 모아 짧은 구매 안내로 정리했다.",
            ),
            keyword_list=("뉴스", "분석", "기술", "도시", "경제"),
            author_names=("김서연", "박준호", "이하늘"),
            section_names=("기술", "도시", "경제", "문화"),
            legacy_encoding="euc-kr",
        ),
        "ar": LocaleContent(
            language_code="ar",
            locale_code="ar_AE",
            site_domain="akhbar-almadina.ae",
            site_title="أخبار المدينة",
            headlines=(
                "باحثون يقدمون طريقة أرخص لتخزين الطاقة في الشبكة",
                "المجلس البلدي يوافق على إعادة تأهيل الواجهة البحرية",
                "ارتفاع رواتب قطاع البرمجيات بنسبة اثني عشر بالمئة",
                "كيف تختار دراجة مناسبة للتنقل اليومي",
            ),
            descriptions=(
                "تحليل مفصل يعتمد على بيانات مفتوحة وشهادات العاملين في القطاع.",
                "ما الذي يتغير بالنسبة للسكان وكم تبلغ الكلفة ومتى تنتهي الأعمال.",
                "دراسة كاملة للسوق مع رسوم بيانية وتوقعات للعام المقبل.",
            ),
            paragraphs=(
                "يقول فريق البحث إن الطريقة تضاعف تقريبا كثافة الطاقة من دون زيادة تذكر في كلفة التصنيع.",
                "أكدت الجهة المختصة أن أي قرار نهائي لن يصدر قبل انتهاء جلسات الاستماع والتقييم المستقل.",
                "يشير المحللون إلى تحول الطلب نحو المهندسين ذوي الخبرة بينما تتراجع وظائف المبتدئين.",
                "جمعنا أسئلة القراء وحولناها إلى دليل شراء مختصر.",
            ),
            keyword_list=("أخبار", "تحليل", "تقنية", "مدينة", "اقتصاد"),
            author_names=("ليلى الحارثي", "سامي القاسمي", "نور الدين بلعيد"),
            section_names=("تقنية", "مدينة", "اقتصاد", "ثقافة"),
            text_direction="rtl",
        ),
        "he": LocaleContent(
            language_code="he",
            locale_code="he_IL",
            site_domain="hadashot-hair.co.il",
            site_title="חדשות העיר",
            headlines=(
                "חוקרים הציגו שיטה זולה יותר לאגירת אנרגיה",
                "מועצת העיר אישרה את שיפוץ הטיילת",
                "השכר בענף התוכנה עלה בשנים עשר אחוזים",
                "איך בוחרים אופניים לנסיעה יומית לעבודה",
            ),
            descriptions=(
                "ניתוח מעמיק המבוסס על נתונים פתוחים ועל דברי אנשי המקצוע.",
                "מה משתנה עבור התושבים, כמה זה עולה ומתי העבודות מסתיימות.",
                "סקר שוק מלא עם גרפים, נתוני גלם ותחזית לשנה הקרובה.",
            ),
            paragraphs=(
                "לדברי צוות המחקר השיטה כמעט מכפילה את צפיפות האנרגיה בלי לייקר את הייצור.",
                "הרשות הדגישה שלא תתקבל החלטה סופית לפני סיום השימועים והבדיקה החיצונית.",
                "אנליסטים מציינים מעבר למפתחים מנוסים בעוד משרות הכניסה מצטמצמות שלושה רבעונים.",
                "אספנו את שאלות הקוראים והפכנו אותן למדריך קנייה קצר.",
            ),
            keyword_list=("חדשות", "ניתוח", "טכנולוגיה", "עיר", "כלכלה"),
            author_names=("נועה שגב", "איתי ברזילי", "רותם אלמוג"),
            section_names=("טכנולוגיה", "עיר", "כלכלה", "תרבות"),
            text_direction="rtl",
            legacy_encoding="windows-1255",
        ),
    }
)
