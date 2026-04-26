CREATE DATABASE IF NOT EXISTS kids_explorer
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE kids_explorer;

CREATE TABLE subjects (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(50)  NOT NULL COMMENT '中文名，如 熊猫',
  name_en     VARCHAR(100) NOT NULL COMMENT '英文名，如 giant panda',
  emoji       VARCHAR(10)  NOT NULL,
  category    ENUM('food','animal','plant') NOT NULL,
  sub_category VARCHAR(20) NOT NULL COMMENT '子分类，如 陆地',
  seed        INT UNSIGNED NOT NULL COMMENT '图像生成随机种子',
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_category (category),
  INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE images (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  subject_id  BIGINT UNSIGNED NOT NULL,
  view_type   ENUM('single','front','back','left','right',
                   'front_left','front_right','back_left','back_right') NOT NULL,
  image_url   TEXT NOT NULL COMMENT '图像 URL 或 Base64',
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
  INDEX idx_subject (subject_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE parts (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  subject_id  BIGINT UNSIGNED NOT NULL,
  image_id    BIGINT UNSIGNED NOT NULL COMMENT '对应哪张视角图',
  part_key    VARCHAR(50)  NOT NULL COMMENT '部位标识，如 eye_patch',
  name        VARCHAR(50)  NOT NULL COMMENT '中文部位名，如 黑眼圈',
  short_name  VARCHAR(5)   NOT NULL COMMENT '1字简称，如 眼',
  color       VARCHAR(10)  NOT NULL COMMENT '标注颜色，如 #4FC3F7',
  pos_x       DECIMAL(4,3) NOT NULL COMMENT '标注点 x 坐标（0~1）',
  pos_y       DECIMAL(4,3) NOT NULL COMMENT '标注点 y 坐标（0~1）',
  description TEXT         NOT NULL COMMENT '部位介绍文字',
  facts       JSON         NOT NULL COMMENT '{"颜色":"黑色","习性":"...","趣味":"..."}',
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
  FOREIGN KEY (image_id)   REFERENCES images(id)   ON DELETE CASCADE,
  INDEX idx_subject (subject_id),
  INDEX idx_image   (image_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE history (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  subject_id  BIGINT UNSIGNED NOT NULL,
  category    ENUM('food','animal','plant') NOT NULL,
  explored_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
  INDEX idx_category    (category),
  INDEX idx_explored_at (explored_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
