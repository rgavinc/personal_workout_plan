(function () {
  const title =
    document.querySelector(".reset.ffGothamBlack.exTtl")?.textContent.trim() ||
    "No title found";
  const mainImg =
    document.querySelector(".imgWrp.exWrp.hasAnim img")?.src ||
    "No main image found";

  const muscleBlocks = document.querySelectorAll(".left.metaWrp .metaBlock");
  const muscleLines = [];

  muscleBlocks.forEach((block) => {
    const key = block.querySelector(".metaKey")?.textContent.trim();
    if (!key || key.toLowerCase().includes("equipment")) return;

    const vals = [...block.querySelectorAll(".metaVal a")].map((a) =>
      a.textContent.trim(),
    );
    if (vals.length) muscleLines.push(`${key}: ${vals.join(", ")}`);
  });

  const description =
    document.querySelector(".right.ffGothamBook.cntWrp")?.textContent.trim() ||
    "No description found";

  console.log(
    `TITLE:
${title}

MAIN IMAGE:
${mainImg}

MUSCLES WORKED:
${muscleLines.join("\n")}

DESCRIPTION:
${description}`,
  );
})();
