import type { Block, Post } from "./types";

const zh: Block[] = [
  {
    t: "p",
    x: "如果你和我一样，会觉得新年决心很蠢。多数人改变生活的方式完全错了。他们定这些决心，是因为别人都在定。我们从地位游戏里造出一种浅层意义，但它够不上真正的改变。真正的改变，比说服自己「今年要更自律、更高效」深得多。",
  },
  {
    t: "p",
    x: "如果你就是这样的人，我不是来贬低你的。我放弃的目标比做成的多十倍。我觉得多数人应当如此。但另一件事也成立：人们试着改变生活，几乎每次都彻底失败。",
  },
  {
    t: "p",
    x: "尽管如此，回头看你讨厌的生活，再把自己推向好得多的东西，仍然是明智的。无论你想创业、改造身体，还是走向更有意义的生活并且不在两周后放弃，下面是 7 个关于行为改变、心理和生产力的想法。协议放在最后，挖到你真正想要的生活，大约要一整天。效果会比这一天长得多。",
  },
  { t: "h2", id: "i", x: "I. 你不在想去的地方，因为你还不是那个会在那里的人" },
  {
    t: "p",
    x: "设定大目标时，人通常只盯着成功的两个条件之一。",
  },
  {
    t: "ol",
    items: [
      "改变行动，以便朝目标前进。这是次要的，二阶。",
      "改变你是谁，于是行为自己跟上。这是主要的，一阶。",
    ],
  },
  {
    t: "p",
    x: "多数人设一个表层目标，给自己打气，撑过前几周，然后不怎么挣扎就回到旧方式。他们想在腐烂的地基上盖好生活。",
  },
  {
    t: "p",
    x: "想一个成功的人：身材很好的健美者，身家数亿的创始人，或者走进一群人也不紧张的人。健美者需要咬牙才能吃得健康吗？首席执行官需要纪律才能出现并带领团队吗？表面看像是。实际上，他们看不见自己以另一种方式生活。健美者要咬牙，才能吃得不健康。首席执行官要强迫自己在闹钟之后继续躺着，而且每一秒都讨厌这样。这里有细微差别，先顺着这个例子看。",
  },
  {
    t: "p",
    x: "有人觉得作者的生活极端、自律。对他来说这是自然的。他不是拿来和别的生活方式对比。他就是喜欢这样过。母亲让他休息、出去玩，他忍住没说：「如果我不是在享受，我为什么还在做这件事？」",
  },
  {
    t: "q",
    x: "如果你想要生活里的某个具体结果，你必须先过上创造这个结果的生活方式，而且要在到达结果之前很久就开始。",
  },
  {
    t: "p",
    x: "有人说想减掉 30 磅。作者常常不信。不是因为对方没能力，而是同一个人太常说：「我等不及减完，好重新开始享受生活。」如果你不把导致减重的生活方式过成一生，也找不到一个引力比旧方式更强的理由，你就会回到起点，并且浪费掉拿不回来的资源：时间。",
  },
  {
    t: "p",
    x: "当你真正改变，那些不推动目标的习惯会变得令人厌恶，因为你清楚这些动作会复利成什么样的生活。你能接受现在的标准，是因为你还不完全知道它们是什么、会通向哪里。你说想改变，说想财务自由、想变健康，行动却不是这样。原因比你以为的深。",
  },
  { t: "h2", id: "ii", x: "II. 你不在想去的地方，因为你并不想去那里" },
  {
    t: "q",
    x: "只相信运动。生活发生在事件的层面，不发生在言辞的层面。相信运动。",
    by: "Alfred Adler",
  },
  {
    t: "p",
    x: "要改变你是谁，先得理解心智如何工作，才能开始重写它。第一步：所有行为都指向目标。这是目的论。向前走，是因为你要到达某个位置。挠鼻子，是因为你要让痒消失。这些很清楚。多数时候目标是无意识的。午后坐在沙发上，你可能是在下一项责任到来之前烧掉时间。",
  },
  {
    t: "p",
    x: "再深一层，人会追求伤害自己的目标，再用社会上说得过去、也不让自己显得失败的理由把它包起来。停不了拖延，你也许解释成「缺少纪律」。实际上你仍在追求一个目标：保护自己，不承受做完并公开作品之后的评判。",
  },
  {
    t: "p",
    x: "你说想辞掉没有出路的工作，却没有任何真实理由地留着。你开始以为自己不够有勇气，或者从来不是冒险的人。真实情况是，你在追求安全、可预测，以及一个借口：在那些把这份工作看成成功的人面前，不要看起来像失败者。",
  },
  {
    t: "p",
    x: "真正的改变要求改变目标。不是因为「设定目标」这个动作本身服务于另一个正在伤害你的无意识目标。那一套生产力内容已经说得够多。这里指的是改变观点。目标就是对未来的一次投射，它变成感知的镜头，让你注意到有助于到达那里的信息、想法和资源。",
  },
  { t: "h2", id: "iii", x: "III. 你不在想去的地方，因为你害怕到那里" },
  {
    t: "q",
    x: "一个想法从哪里来并不重要。只要你接受了它，并且确信它为真，它就和催眠师的话对受术者一样有力量。",
    by: "Maxwell Maltz",
  },
  { t: "h3", id: "anatomy", x: "身份的解剖" },
  {
    t: "ol",
    items: [
      "你想达成一个目标。",
      "你透过这个目标看现实。",
      "你只注意到有助于达成它的信息和想法。这是学习。",
      "你朝它行动，并收到「正在前进」的反馈。",
      "你重复这个行为，直到它变成自动的、无意识的。这是条件作用。",
      "这个行为变成你以为的自己：「我是那种会……的人。」",
      "你保卫这个身份，以维持心理一致。",
      "身份塑造新目标，循环重新开始。如果这个身份不利于好的生活，事情会很快变糟。",
    ],
  },
  {
    t: "p",
    x: "必须打断第 6 步和第 7 步之间的循环。这个过程从童年就开始。你的目标是生存。你依赖父母教你如何生存，于是你顺从。多数教导靠奖和罚。不采纳他们的信念和价值，你就会受罚。在看穿这一点之前，你并不是在为自己思考。",
  },
  {
    t: "p",
    x: "父母也走过同一条路。如果他们没有打破模式，他们被工业时代被接受的成功观念塑造，也带着上一代最好和最坏的条件作用。身体的生存需要一旦满足（在今天的世界里这相当容易），生存就转到概念和意识形态层面。你也许不再拼命保护身体，但你会保护并复制你的心智。身份感到威胁时，和身体感到威胁时一样，会进入战斗或逃跑。",
  },
  {
    t: "p",
    x: "你如果强烈认同某种政治意识形态，别人挑战你的信念时，你会感到压力，情绪上像被扇了一耳光。多数人不检验情绪是否为真，于是困在回声里，并加倍坚持伤害自己和他人的主张。在宗教家庭里长大而未为自己思考的人，会攻击威胁那个小气泡里心理安全的人。当你无意识地把自己看成律师、游戏玩家，或任何不会采取行动去过更好生活的人，同一件事也会发生。",
  },
  { t: "h2", id: "iv", x: "IV. 你想要的生活，位于心智的某一层" },
  {
    t: "p",
    x: "心智按可预期的阶段演化。出生时你像一块求生的海绵，吸收文化规定的信念，以便感到安全。如果不小心，心智会结晶，有意义的生活就变难。马斯洛、Greuter 的自我发展、螺旋动力学和整合理论都记录过这些阶段，彼此叠加。作者把它们收进自己的 Human 3.0 模型。下面是自我发展 9 个阶段的八二开。",
  },
  {
    t: "ol",
    items: [
      "冲动。冲动和行动没有分离。非黑即白。幼儿生气就打人，因为感受和行为是同一件事。",
      "自我保护。世界是危险的，你学会照看自己。孩子学会藏成绩单、对家务说谎、弄清大人想听什么。",
      "顺从。你就是你的群体，规则感觉像现实本身。有人真心无法理解为什么有人会和家人投不一样的票。",
      "自我觉察。你注意到内在生活和外在并不一致。坐在教堂里，发现自己不确定是否相信周围的人似乎都相信的东西，但还不知道拿这种感觉怎么办。",
      "尽责。你建立自己的原则，并让自己对它负责。仔细研究后离开家庭宗教，或做出有里程碑的职业计划，因为你相信正确的努力会得到正确的结果。",
      "个体主义。你看见原则是被情境塑造的，开始把它们拿松一点。政治观点更多和成长地有关，而不是客观真理；雄心其实是为了得到父亲的认可。",
      "策略家。你与系统一起工作，同时知道自己也在系统里。带领组织时主动追问自己的盲点。",
      "建构觉察。你把所有框架，包括身份，看成有用的虚构。地图不是领土。看着自己扮演「创始人」，带着一点温和的好笑。",
      "合一。自我与生活的分离消解。工作、休息和玩感觉是同一件事。不再有一个需要变成什么的人，只是对正在发生的事的在场回应。",
    ],
  },
  {
    t: "p",
    x: "作者假设多数读者落在第 4 到第 8 阶段之间，跨度很大。靠近 8 的人读这篇，是为了学一点东西，或以不具破坏性的方式打发时间。靠近 4 的人是真的在找改变。你觉得自己应当有更多，但还无法把一切理顺。好消息是：你在哪一阶段并不那么重要，因为穿过任何一阶段都遵循同一种模式。",
  },
  { t: "h2", id: "v", x: "V. 智能，是从生活中得到你想要的东西的能力" },
  {
    t: "q",
    x: "智能唯一真实的检验，是你能否从生活中得到你想要的。",
    by: "Naval Ravikant",
  },
  {
    t: "p",
    x: "成功有一个配方。一个成分是能动性（agency）。一个成分是机会。很多人喜欢把机会误称为特权，因为他们缺另外的成分。最后一个成分是智能。能动性高而机会低，你再愿意行动也得不到多少果实。机会和能动性都有、智能低，你就无法充分用上那个机会。",
  },
  {
    t: "p",
    x: "作者无法叫你改掉物理位置。但如果数字机会就在面前你却看不见，他也无话可说。这一节聚焦智能，借助控制论。Cybernetics 来自希腊语 kybernetikos，意思是「掌舵」或「善于掌舵」。它也被称为「得到你想要的东西的技艺」。",
  },
  {
    t: "ul",
    items: [
      "有一个目标。",
      "朝目标行动。",
      "感知你在哪里。",
      "把它和目标比较。",
      "根据反馈再行动。",
    ],
  },
  {
    t: "p",
    x: "可以按系统迭代、并用试错坚持下去的能力来判断智能。船被吹离航线后修正向目的地。恒温器感到温度变化就打开。胰腺在血糖升高后分泌胰岛素。高智能是迭代、坚持，并理解大局。低智能的标志，是不能从错误里学习。低智能的人卡在问题上，撞到路障就退出。高智能认识到，在足够长的时间尺度上，任何问题都可以被解决。想法是分层的。你不能从纸莎草一步跳到 Google 文档。眼下做不到，只是还没有资源。资源也许会在接下来几年被发明出来。",
  },
  {
    t: "p",
    x: "这里的「目标」不是典型自助书的镜头，尽管那个镜头有时有用。这里是目的论，希腊语里的 kosmos：一切都服务于一个目的，一切都是更大整体的一部分。目标决定你如何看世界，也决定你把什么当成成功或失败。你可以试着享受旅程，但如果追的是错的目标，你不会享受。心智是现实的操作系统。这个系统由目标组成。对多数人，目标是被指派的，像写进心理的代码：去上学，找到工作，感到被冒犯，扮演受害者，65 岁退休。这是一条已知的、并不奏效的路。",
  },
  {
    t: "ul",
    items: [
      "拒绝已知的路。",
      "进入未知。",
      "设定新的、更高的目标，以扩展心智。",
      "接纳混乱，允许生长。",
      "研究自然的一般原则。",
      "成为一个有深度的通才。",
    ],
  },
  { t: "h2", id: "vi", x: "VI. 如何在一天内进入一种全新的生活" },
  {
    t: "q",
    x: "我人生里最好的时期，总是出现在我彻底受够了自己毫无进展之后。",
  },
  {
    t: "p",
    x: "如何挖进自己的心智，看见条件作用，并到达能改变轨迹的洞见？靠提问。很少有人真正提问。你听他们怎么谈论一个题目就能知道。提问就是思考。",
  },
  {
    t: "p",
    x: "下面是一份可以每年用来重置生活的协议。它从大到小：你想在哪里，需要做什么才能到那里，以及立刻可以做什么。它需要一整天。准备笔、纸，和一个开放的头脑。不要把这番思考外包给 AI。",
  },
  {
    t: "p",
    x: "成功翻转身份的人，往往在张力积到足够之后很快发生。常见三相：失调，觉得自己不属于当前的生活，并且受够了没有进展；不确定，不知道下一步，于是试验，或者迷路并感觉更差；发现，找到要追求的东西，并在 6 个月里做出 6 年的进展。协议的目的，是帮你到达失调，穿过不确定，并发现你真正想达成的事，清晰到干扰不再有分量。",
  },
  {
    t: "p",
    x: "作者不能保证对每个人有效。不能把故事的高潮放在开头，还指望它有意思。你得处在自己故事里合适的那一章。",
  },
  { t: "h3", id: "morning", x: "上午：心理挖掘，愿景与反愿景" },
  {
    t: "p",
    x: "先为心智造一个新的框架，也就是新的感知镜头。像造一个新壳，离开旧壳，再慢慢长进去。一开始会觉得不合身。这是好事。留出 15 到 30 分钟。答不上来就稍后回来。",
  },
  {
    t: "ol",
    items: [
      "你已经学会与之共处的、沉闷而持续的不满是什么？不是深重的苦，而是你学会容忍的东西。如果你不恨它，你就会容忍它。",
      "你反复抱怨、却从未真正改变的是什么？写下过去一年你说得最多的三句抱怨。",
      "对每一句抱怨：一个只看你的行为、不听你的话的人，会断定你实际上想要什么？",
      "关于你当前的生活，有什么真相是你无法向深深尊敬的人承认的？",
      "如果未来五年绝对没有任何改变，描述一个普通的星期二。你在哪里醒来？身体什么感觉？第一个念头是什么？周围是谁？上午 9 点到下午 6 点你做什么？晚上 10 点你感觉如何？",
      "再写十年。你错过了什么？哪些机会关上了？谁放弃了你？你不在房间时，人们怎么说你？",
      "你在生命的尽头。你过的是安全版本。你从未打破模式。代价是什么？你从未允许自己感受、尝试或成为的是什么？",
      "谁已经活在你刚刚描述的未来里？在同一条轨迹上超前五年、十年或二十年的人。想到自己变成他们，你感觉如何？",
      "为了真正改变，你必须放弃哪个身份？「我是那种会……的人。」不再做那个人，社会成本是什么？",
      "你还没改变的最难堪的原因是什么？那个让你听起来软弱、害怕或懒，而不是听起来合理的原因。",
      "如果当前行为是一种自我保护，你到底在保护什么？这种保护让你付出什么？",
      "忘掉可行性一分钟。如果你能打个响指，三年后过上另一种生活，不是「现实的」，而是你实际上想要的。一个普通星期二是什么样？细节和上一问相同。",
      "为了让那种生活感觉自然而不是勉强，你必须相信自己是什么样的人？写下：「我是那种会……的人。」",
      "如果你已经是那个人，这周你会做的一件事是什么？",
    ],
  },
  {
    t: "p",
    x: "前四问让你看见当前生活里的痛。后面把它们变成反愿景：对你不想过的生活的无情觉察。这样你可以用这股负能量把努力瞄准正方向，并从内在动机出发。如果答得诚实，而且你处在合适的章节，你会对现在的生活感到深深的不安，甚至厌恶。然后把这股能量转到一个最小可用愿景上。愿景像产品，一开始不清楚，随时间和经验变强。",
  },
  { t: "h3", id: "day", x: "白天：打断自动驾驶" },
  {
    t: "p",
    x: "写日记很可爱，但不会带来真改变，除非你打断那些让你保持原样的无意识模式。你不会靠把同一件事做到底来改变。现在就在手机里建提醒或日历，把问题写进提醒里。越随机、越不和日程冲突越好。通勤、走路或躺着时，再想附加的三问。",
  },
  {
    t: "ul",
    items: [
      "上午 11:00：我现在做这件事，是在逃避什么？",
      "下午 1:30：如果有人拍下过去两小时，他们会断定我想从生活里得到什么？",
      "下午 3:15：我在走向我讨厌的生活，还是我想要的生活？",
      "下午 5:00：我假装不重要的、最重要的事是什么？",
      "晚上 7:30：今天我做的哪些事是出于身份保护，而不是真正的愿望？提示：多数事情都是。",
      "晚上 9:00：今天我何时最有生气？何时最像死了？",
      "如果我不再需要别人把我看成第 10 问里的那个身份，什么会改变？",
      "我在生活的哪里用生气换安全？",
      "明天我能成为的、我想成为的那个人的最小版本是什么？",
    ],
  },
  { t: "h3", id: "night", x: "晚上：综合洞见，进入一段进展期" },
  {
    t: "p",
    x: "如果按过程做了，至少会有一个能改变轨迹的洞见。接下来要让它被知道，整合进你是谁，并据此行动。目标在这里不是为了成就而设。目标只是投射，不可靠，还会把你绑在必然会变的东西上。把目标想成观点，一副可以换上的镜头，让你进入正确的心智状态，去做那件离开不想要的生活的事。不要担心终点线。享受在进展里。",
  },
  {
    t: "ol",
    items: [
      "经过今天，关于你为什么卡住，什么感觉最真实？",
      "真正的敌人是什么？说清楚。不是处境，不是别人。是那个一直在运转的内在模式或信念。",
      "写一句话，抓住你拒绝让生活变成的样子。这是压缩后的反愿景。读的时候应当有感觉。",
      "写一句话，抓住你正在建向的东西，并知道它会演化。这是愿景的最小可用版本。",
      "一年镜头：一年后，什么必须为真，你才知道旧模式已经破了？一件具体的事。",
      "一月镜头：一个月后，什么必须为真，一年镜头才仍然可能？",
      "每日镜头：明天可以放进时间块的 2 到 3 个行动是什么？正在成为的那个人会直接去做。",
    ],
  },
  { t: "h2", id: "vii", x: "VII. 把生活变成一局游戏" },
  {
    t: "q",
    x: "内在经验的最佳状态，是意识里有秩序。当注意力投在现实的目标上，并且技能与行动机会相称时，这就会发生。",
    by: "Mihaly Csikszentmihalyi",
  },
  {
    t: "p",
    x: "你已经有了通向好生活的组件。把洞见收成一份连贯的计划。新的一页，写下六项。",
  },
  {
    t: "ul",
    items: [
      "反愿景：我存在的祸根，或我再也不想经历的生活。这是赌注。输了或放弃会怎样。",
      "愿景：我认为想要、并且可以在朝它工作时改进的理想生活。这是如何获胜，直到游戏演化。",
      "一年目标：一年后生活是什么样，它是否更接近我想要的生活。这是任务，是眼下唯一的优先级。",
      "一月项目：我需要学什么、获得什么技能、可以建造什么。这是头目战，你在这里获得经验和战利品。",
      "每日杠杆：推动项目完成的优先事项。这是任务，是每天解锁新机会的过程。",
      "约束：为了从零建起愿景，我不愿意牺牲什么。这是规则，限制促成创造。",
    ],
  },
  {
    t: "p",
    x: "这些组件真的会造出一个小世界。如果在生命的这一阶段你应当追求这层目标，你将没有别的选择，只能着迷。你会感到被更大的东西拉住。其他东西不再像选项。",
  },
  {
    t: "p",
    x: "游戏是痴迷、享受和心流的样板。它们具备带来专注和清晰的全部组件。把这些组件逆向出来，就可以活在更深的享受、更少的干扰和更多的成功里。六项像一组同心圆，像力场，挡住干扰和闪亮的新东西。你玩得越久，这股力越强，很快它就变成你是谁。你也不会想要别的方式。",
  },
  {
    t: "note",
    x: "中文为按原文结构完成的译文，遵循中文技术文档的用词与留白，不是官方译本。原帖没有配图。引文与阶段名保留原文，不另造替代词。营销订阅段落未收入正文。版权归 Dan Koe。",
  },
];

const en: Block[] = [
  {
    t: "p",
    x: "If you're anything like me, you think New Year's resolutions are stupid. Most people change their lives the wrong way. Resolutions borrow meaning from status games, and they do not meet the requirements for true change.",
  },
  {
    t: "p",
    x: "The author has quit ten times as many goals as he has achieved. He thinks that should be true for most people. It is still wise to look at the life you hate and launch toward something better. Seven ideas follow. The protocol at the end takes about a day.",
  },
  { t: "h2", id: "i", x: "I. You aren't the person who would be there" },
  {
    t: "ol",
    items: [
      "Change your actions. Second order. Least important.",
      "Change who you are, so behavior follows. First order. Most important.",
    ],
  },
  {
    t: "p",
    x: "Surface goals sit on a rotting foundation. A bodybuilder does not grind to eat well; he would have to grind to eat badly. A founder does not discipline himself to show up. If you want an outcome, you need the lifestyle that creates it long before you arrive. “I can't wait to finish losing weight so I can enjoy life again” is a tell that the old goal still has more gravity.",
  },
  { t: "h2", id: "ii", x: "II. You don't want to be there" },
  {
    t: "q",
    x: "Trust only movement. Life happens at the level of events, not of words.",
    by: "Alfred Adler",
  },
  {
    t: "p",
    x: "All behavior is goal-oriented, and most goals are unconscious. Procrastination can be the goal of avoiding judgment. Staying in a dead-end job can be the goal of safety. Real change means changing your point of view. A goal is a lens that lets you notice what helps.",
  },
  { t: "h2", id: "iii", x: "III. You're afraid to be there" },
  {
    t: "q",
    x: "An idea you accept as true has the same power as a hypnotist's words.",
    by: "Maxwell Maltz",
  },
  {
    t: "p",
    x: "Identity: want a goal, see through it, notice only what helps, act, condition the behavior, call it “the type of person I am,” defend it, then let it set the next goal. Survival training starts in childhood. Once the body is safe, people survive on the conceptual level. A threatened identity triggers fight or flight.",
  },
  { t: "h2", id: "iv", x: "IV. A specific level of mind" },
  {
    t: "p",
    x: "Nine ego stages, compressed: Impulsive, Self-Protective, Conformist, Self-Aware, Conscientious, Individualist, Strategist, Construct-Aware, Unitive. Most readers sit between 4 and 8. The stage matters less than the pattern of moving through one.",
  },
  { t: "h2", id: "v", x: "V. Intelligence" },
  {
    t: "q",
    x: "The only real test of intelligence is if you get what you want out of life.",
    by: "Naval Ravikant",
  },
  {
    t: "p",
    x: "Success is agency, opportunity, and intelligence. Cybernetics: have a goal, act, sense, compare, act again. Low intelligence cannot learn from mistakes. High intelligence knows there is a hierarchy of choices, and that a long enough timescale changes what is solvable. Reject the known path. Set higher goals. Become a deep generalist.",
  },
  { t: "h2", id: "vi", x: "VI. One day" },
  {
    t: "p",
    x: "Three phases: dissonance, uncertainty, discovery. One day, pen and paper. Do not outsource the thinking to AI. Morning excavates vision and anti-vision. Daytime reminders break autopilot. Evening compresses the insight into lenses, not finish lines.",
  },
  {
    t: "ul",
    items: [
      "11:00 — What am I avoiding by doing what I'm doing?",
      "1:30 — If someone filmed the last two hours, what would they say I want?",
      "3:15 — Toward the life I hate, or the life I want?",
      "5:00 — What important thing am I pretending is not important?",
      "7:30 — What did I do from identity protection?",
      "9:00 — When was I most alive, and most dead?",
    ],
  },
  { t: "h2", id: "vii", x: "VII. A video game" },
  {
    t: "ul",
    items: [
      "Anti-vision — what's at stake.",
      "Vision — how you win.",
      "1 year goal — the mission.",
      "1 month project — the boss fight.",
      "Daily levers — the quests.",
      "Constraints — the rules.",
    ],
  },
  {
    t: "p",
    x: "Together they make a small world and a forcefield against distraction. Play long enough and the game becomes who you are.",
  },
  {
    t: "note",
    x: "English on this page is a structured original-language companion, not a substitute for the X article. Copyright Dan Koe.",
  },
];

export const danKoe: Post = {
  slug: "dan-koe-one-day",
  title: "如何在一天内彻底改变你的人生",
  titleEn: "How to fix your entire life in 1 day",
  dek: "身份先于行动。反愿景、愿景，以及把生活收成一局游戏的一天协议。",
  dekEn: "Identity before action. An anti-vision, a vision, and a one-day protocol that turns a life into a game.",
  author: "Dan Koe",
  date: "2026-01-12",
  minutes: 23,
  source: "https://x.com/thedankoe/status/2010751592346030461",
  sourceName: "X · @thedankoe",
  copyright: "Dan Koe",
  official: false,
  section: "life",
  blocks: zh,
  blocksEn: en,
};
