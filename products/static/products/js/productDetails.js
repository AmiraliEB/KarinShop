
// COLOR SELCET
const colorButtons = document.querySelectorAll(".color-select-btn");
const colorTitle = document.querySelector(".color-title");

colorButtons?.forEach((button) => {
    button.addEventListener("click", () => {
        colorButtons.forEach((btn) => {
            btn.classList.remove("ring-4", "ring-blue-400");
            btn.classList.add("ring-1", "ring-gray-400");
        });

        button.classList.remove("ring-1", "ring-gray-400");
        button.classList.add("ring-4", "ring-blue-400");

        const span = button.querySelector("span");
        const classList = span.classList;
        const colorClass = Array.from(classList).find(c => c.startsWith("bg-"));

        const colorMap = {
            "bg-black": "مشکی",
            "bg-white": "سفید",
            "bg-green-400": "سبز",
            "bg-blue-500": "آبی"
        };

        const colorName = colorMap[colorClass] || "نامشخص";
        colorTitle.textContent = `رنگ : ${colorName}`;
    });
});



// TEXT SLIDER 
document.addEventListener("DOMContentLoaded", () => {
    const texts = [
        { text: "🔥 ۱۰۰۰+ فروش در هفته گذشته", color: "text-red-500" },
        { text: "💯 ۵۰۰+ نفر بیش از ۲ بار این کالا را خریده‌اند", color: "text-green-600" },
        { text: "🛒 در سبد خرید ۱۰۰۰+ نفر", color: "text-blue-600" }
    ];

    let index = 0;
    const slider = document.getElementById("slider-text");

    setInterval(() => {
        index = (index + 1) % texts.length;
        slider.classList.add("opacity-0");

        setTimeout(() => {
            slider.innerHTML = `<p class="${texts[index].color}">${texts[index].text}</p>`;
            slider.classList.remove("opacity-0");
        }, 300);
    }, 3000);
});



// CHANGE TAB 
document.addEventListener("DOMContentLoaded", () => {
    const buttonsTab = document.querySelectorAll(".tab-btn");
    const contents = document.querySelectorAll(".tab-content");

    buttonsTab.forEach((btn) => {
        btn.addEventListener("click", () => {
            const target = btn.getAttribute("data-target");

            buttonsTab.forEach((b) => {
                b.classList.remove("text-blue-500");
                b.classList.add("text-gray-500", "dark:text-gray-300");
            });
            btn.classList.remove("text-gray-500", "dark:text-gray-300");
            btn.classList.add("text-blue-500");

            contents.forEach((content) => {
                if (content.classList.contains(target)) {
                    content.classList.remove("hidden");
                    content.classList.add("block");
                } else {
                    content.classList.remove("block");
                    content.classList.add("hidden");
                }
            });
        });
    });
});




// SHOW MORE COMMENTS
const moreCommentBtn = document.querySelector('.more-comment-btn');
const moreCommentText = document.querySelector('.more-comment-text');
const moreCommentIcon = document.querySelector('.more-comment-icon');
const hiddenCommentItems = document.querySelectorAll('.hidden-comment-item');

if (moreCommentBtn) {
    moreCommentBtn.addEventListener('click', () => {
        hiddenCommentItems.forEach(item => {
            item.classList.toggle('hidden');
            item.classList.toggle('block');
        });

        if (moreCommentText.innerHTML === 'مشاهده بیشتر') {
            moreCommentText.innerHTML = 'مشاهده کمتر';
        } else {
            moreCommentText.innerHTML = 'مشاهده بیشتر';
        }

        moreCommentIcon.classList.toggle('rotate-180');
    });
}




// PRODUCT SLIDER

const openSliderModals = document.querySelectorAll('.open-sliderModal')
const sliderModal = document.querySelector('.slider-modal')
const overlayProductPage = document.querySelector('.overlay')
const closeSliderModal = document.querySelector('.close-sliderModal')

openSliderModals.forEach(el => {
    el.addEventListener('click', () => {
        sliderModal.classList.add('active')
        overlayProductPage.classList.add('active')
    })
})

overlayProductPage.addEventListener('click', () => {
    overlayProductPage.classList.remove('active')
    sliderModal.classList.remove('active')
})

closeSliderModal.addEventListener('click', () => {
    sliderModal.classList.remove('active')
    overlayProductPage.classList.remove('active')
})

// SHOW MORE SPECIFICATIONS
const moreSpecsBtn = document.querySelector('.more-specs-btn');
const moreSpecsText = document.querySelector('.more-specs-text');
const moreSpecsIcon = document.querySelector('.more-specs-icon');
const hiddenSpecItems = document.querySelectorAll('.hidden-spec-item');
const hiddenSpecCategoryGroups = document.querySelectorAll('.hidden-spec-category-group');

if (moreSpecsBtn) {
    moreSpecsBtn.addEventListener('click', () => {
        hiddenSpecItems.forEach(item => {
            item.classList.toggle('hidden');
            item.classList.toggle('block'); 
        });

        hiddenSpecCategoryGroups.forEach(group => {
            group.classList.toggle('hidden');
            group.classList.toggle('block'); 
        });

        if (moreSpecsText.innerHTML === 'مشاهده بیشتر') {
            moreSpecsText.innerHTML = 'مشاهده کمتر';
            moreSpecsIcon.classList.add('rotate-180');
        } else {
            moreSpecsText.innerHTML = 'مشاهده بیشتر';
            moreSpecsIcon.classList.remove('rotate-180');
        }
    });
}
// ===================================================
// INTERACTIVE RATING STARS FOR COMMENT FORM
// ===================================================
document.addEventListener("DOMContentLoaded", () => {
    const starsContainer = document.getElementById("rating-stars-container");
    const ratingStars = document.querySelectorAll(".rating-star");
    const ratingValueInput = document.getElementById("rating-value");
    const recommendBtn = document.getElementById("recommend-btn");
    const dontRecommendBtn = document.getElementById("dont-recommend-btn");
    const recommendValueInput = document.getElementById("recommend-value"); 

    if (!starsContainer || !ratingStars.length || !ratingValueInput || !recommendBtn || !dontRecommendBtn || !recommendValueInput) {
        return;
    }

    let currentRating = 0; 

    const recommendActiveClasses = ["ring-green-600", "dark:ring-green-600"];
    const dontRecommendActiveClasses = ["ring-[#EF4343]", "dark:ring-[#EF4343]"];
    const defaultRingClasses = ["ring-transparent", "dark:ring-white/20"];

    const updateStars = (value) => {
        ratingStars.forEach(star => {
            const starValue = parseInt(star.getAttribute("data-value"));
            if (starValue <= value) {
                star.classList.remove("text-gray-300", "dark:text-gray-600");
                star.classList.add("text-yellow-400");
            } else {
                star.classList.remove("text-yellow-400");
                star.classList.add("text-gray-300", "dark:text-gray-600");
            }
        });
    };

    const selectRecommend = () => {
        recommendBtn.classList.remove(...defaultRingClasses); 
        recommendBtn.classList.add(...recommendActiveClasses); 
        dontRecommendBtn.classList.remove(...dontRecommendActiveClasses);
        dontRecommendBtn.classList.add(...defaultRingClasses);
        recommendValueInput.value = "True";
    };

    const selectDontRecommend = () => {
        dontRecommendBtn.classList.remove(...defaultRingClasses); 
        dontRecommendBtn.classList.add(...dontRecommendActiveClasses); 
        recommendBtn.classList.remove(...recommendActiveClasses);
        recommendBtn.classList.add(...defaultRingClasses);
        recommendValueInput.value = "False";
    };

    ratingStars.forEach(star => {
        star.addEventListener("mouseover", () => {
            const hoverValue = parseInt(star.getAttribute("data-value"));
            updateStars(hoverValue);
        });

        star.addEventListener("click", () => {
            currentRating = parseInt(star.getAttribute("data-value"));
            ratingValueInput.value = currentRating; 
            updateStars(currentRating); 
        });
    });

    recommendBtn.addEventListener("click", () => {
        selectRecommend();
    });

    dontRecommendBtn.addEventListener("click", () => {
        selectDontRecommend();
    });

    starsContainer.addEventListener("mouseout", () => {
        updateStars(currentRating); 
    });
});